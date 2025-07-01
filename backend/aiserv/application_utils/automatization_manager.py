 
import time

from typing import Any, Dict, List, Optional
from django.db import close_old_connections
from django.utils.timezone import now as django_now, timedelta as django_timedelta
from langchain.agents import initialize_agent, AgentType

from .agent.openai_agent import OpenaiAgent
from ..auth_utils import check_existing_tokens, initialize_services
from ..models import HistoryConfig, aiservUser
from .email_utils import EmailProcessor
from ..utils import flow_notification_to_front
from .calendar_utils import CalendarUtils

class EmailAutomationManager:
    """
    Clase orquestadora que inicializa servicios, configura el usuario y ejecuta el ciclo de verificación de correos.
    """

    def __init__(self, user_id: int) -> None:
        """
        Inicializa la automatización: obtiene el usuario, credenciales y servicios.
        
        Args:
            user_id (int): ID del usuario.
        """
        self.user_id = user_id
        self.user = aiservUser.objects.get(id=user_id)
        credentials = check_existing_tokens(self.user)
        if not credentials:
            raise ValueError(f"No se pudieron obtener o actualizar las credenciales para {self.user.email}.")
        self.gmail_service, self.calendar_service, self.oauth_service = initialize_services(credentials)
        self.calendar_utils = CalendarUtils(self.calendar_service, self.user)
        self.processor = EmailProcessor(self.user, self.gmail_service)
        self.label_ids = self.processor.get_label_ids()
        self.label_superior_id = self.label_ids.get('superior')
        self.label_companero_id = self.label_ids.get('compañero')
        self.label_clientes_importante_id = self.label_ids.get('cliente importante')
        self.label_nuevos_clientes_id = self.label_ids.get('nuevo cliente')

    def run(self) -> None:
        """
        Ejecuta el ciclo principal de verificación y procesamiento de correos.
        """
        while True:
            close_old_connections()
            self.user.refresh_from_db()
            if not self.user.is_active_auto:
                print(f"El usuario {self.user.email} ha desactivado la autogestión. Deteniendo verificación.")
                break

            if self.gmail_service and self.calendar_service:
                try:
                    print(f"Procesando correos para {self.user.email}")
                    messages: List[Dict[str, Any]] = []
                    if self.label_superior_id:
                        messages += self.processor.read_emails_with_label(self.label_superior_id, label_name="superior")
                    if not messages and self.label_companero_id:
                        messages += self.processor.read_emails_with_label(self.label_companero_id, label_name="compañero")
                    if not messages and self.label_clientes_importante_id:
                        messages += self.processor.read_emails_with_label(self.label_clientes_importante_id, label_name="cliente importante")
                    if not messages and self.label_nuevos_clientes_id:
                        messages += self.processor.read_emails_with_label(self.label_nuevos_clientes_id, label_name="nuevo cliente")
                    if not messages:
                        messages += self.processor.read_emails_without_label()

                    if not messages:
                        print("No se encontraron correos sin leer.")
                        time.sleep(60)
                        continue

                    for entry in messages:
                        msg = entry.get("message")
                        label = entry.get("label")
                        email_data: Dict[str] = self.processor.process_email(msg)
                        
                        try:

                            agent_builder = OpenaiAgent(self.gmail_service, self.calendar_service, self.user_id,email_data)
                            agent = initialize_agent(
                                tools=agent_builder.get_tools(),
                                llm=agent_builder.get_llm(),
                                agent=AgentType.OPENAI_FUNCTIONS,
                                verbose=True,
                                prompt=agent_builder.get_prompt(),
                                handle_parsing_errors=True,
                            )

                            output = agent.invoke({"input": email_data})
                            print(output)
                        except Exception as e:
                            print(f"Agent Error: {e}")

                        self.processor.mark_as_read(email_data["id"])

                        # Se registran notificaciones y se guarda el historial
                        HistoryConfig.objects.create(
                            gmail=self.user.email,
                            sender=self.processor._extract_email(email_data.get("Sender", "")),
                            subject=email_data.get("Subject", "Sin asunto"),
                            summary=' '.join(email_data.get("Body", "").split()[:15]),
                            sent_date=django_now(),
                            expire_date=django_now() + django_timedelta(days=5)
                        )
                        flow_notification_to_front(
                            gmail=self.user.email,
                            sender=self.processor._extract_email(email_data.get("Sender", "")),
                            subject=email_data.get("Subject", "Sin asunto"),
                            body=email_data.get("Body", ""),
                            type="", # VER COMO SE PUEDE MANEJAR ESTO
                            label=label
                        )
                except Exception as e:
                    print(f"Error procesando correos para {self.user.email}: {e}")
            else:
                print(f"Error: No se pudieron inicializar los servicios de Gmail o Calendar para {self.user.email}")
            time.sleep(60)