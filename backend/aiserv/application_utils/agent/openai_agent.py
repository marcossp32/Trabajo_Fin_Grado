from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
from langchain.tools import Tool
from langchain_core.tools.structured import StructuredTool

from ...text_feeling import analizar_texto
from ..email_utils import EmailTools
from ..calendar_utils import CalendarUtils
from ...models import aiservUser

class EmailResponseInput(BaseModel):
    response: str = Field(
        description="Respuesta al correo con un lenguaje amigable y sencillo"
    )

class AvailabilityInput(BaseModel):
    date: str = Field(
        description="Fecha del evento en formato RFC3339. Ej: '2025-04-02T12:00:00+02:00'"
    )

class GenerateEventInput(BaseModel):
    date: str = Field(
        description="Fecha y hora de inicio del evento en formato ISO 8601. Ej: '2025-04-02T12:00:00+02:00'."
    )
    duration: Optional[str] = Field(
        default=None,
        description="Duración del evento en lenguaje natural, por ejemplo '1 hour' o '30 minutes'."
    )
    participants: Optional[List[str]] = Field(
        default_factory=list,
        description="Lista de emails de los participantes. Recuerda incluir al remitente si es necesario."
    )
    event_type: Optional[str] = Field(
        default="Meeting",
        description="Tipo de evento, por defecto 'Meeting'."
    )
    place: Optional[str] = Field(
        default=None,
        description="Lugar físico donde se celebrará el evento."
    )
    meeting_link: Optional[str] = Field(
        default=None,
        description="Enlace a videollamada si aplica."
    )
    priority: Optional[str] = Field(
        default=None,
        description="Prioridad del evento, por ejemplo 'Alta', 'Media' o 'Baja'."
    )
    attachments: Optional[List[str]] = Field(
        default_factory=list,
        description="Enlaces a archivos relacionados con el evento."
    )
    deadline: Optional[str] = Field(
        default=None,
        description="Fecha límite en formato ISO 8601, si aplica."
    )
    details: Optional[str] = Field(
        default=None,
        description="Información adicional o descripción larga del evento."
    )

class FindEventInput(BaseModel):
    previous_event_date: str = Field(
        description="Fecha del evento que se quiere cambiar en formato RFC3339. Ej: '2025-04-02T12:00:00+02:00'"
    )

class ChangeEventInput(BaseModel):
    event_id: str = Field(
        description="ID del evento obtenido de la tool FindEvent."
    )
    new_event_date: str = Field(
        description="Nueva fecha propuesta en formato RFC3339. Ej: '2025-04-02T12:00:00+02:00'."
    )
    duration: Optional[str] = Field(
        default='30',
        description="Duración de la reunión, si se incluye."
    )

class CancelEventInput(BaseModel):
    event_id: str = Field(
        description="ID del evento obtenido de la tool FindEvent."
    )


class OpenaiAgent:        
    
    def __init__(self, gmail_service: Any, calendar_service: Any, user_id: int, email_data: Dict[str, Any]) -> None:
        """
        Inicializa el procesador con el usuario y los servicios de Gmail y Calendar.
        """
        self.user = aiservUser.objects.get(id=user_id)
        self.llm = ChatOpenAI(model="gpt-4", temperature=0.3)
        self.email_tools = EmailTools(self.user, gmail_service, calendar_service)
        self.calendar_tools = CalendarUtils(calendar_service, self.user)
        self.user_id = user_id
        self.email_data = email_data

    def send_response_tool(self, response: Any):
        try:
            if isinstance(response, str):
                parsed_input = EmailResponseInput(response=response)
            elif isinstance(response, dict):
                parsed_input = EmailResponseInput.model_validate(response)
            elif isinstance(response, EmailResponseInput):
                parsed_input = response
            else:
                raise ValueError("Tipo de input no soportado. Debe ser un string o diccionario.")
        except Exception as e:
            return f"Error en la validación del input: {e}"
        return self.email_tools.send_email_response(self.email_data, parsed_input.response)

    
    def generate_event_tool(self, input: GenerateEventInput):
        # Verificamos que el campo "date" esté presente
        if not input.date:
            return "Error: el campo 'date' es obligatorio."
        # Convertir el input a diccionario para pasarlo a la tool de calendario
        event_data = input.model_dump()
        sender = self.email_data["Sender"]
        subject = self.email_data["Subject"]
        return self.calendar_tools.generate_event(event_data=event_data, sender=sender, subject=subject, user=self.user)
    

    def change_event_tool(self, input: ChangeEventInput):
        # Verificamos que el campo "date" esté presente
        if not input.event_id or not input.duration or not input.new_event_date:
            return "Faltan campos"
        
        return self.calendar_tools.change_event(input.new_event_date, input.duration, input.event_id,self.user)
        

    def get_tools(self) -> List[Tool]:
        return [
            StructuredTool(
                name="SendEmailResponse",
                func=self.send_response_tool, 
                description="Envía una respuesta por correo electrónico. Se debe proveer el campo 'response'. Se usará el email_data del __init__.",
                args_schema=EmailResponseInput
            ),
            StructuredTool(
                name="CheckCalendarAvailability",
                func=self.email_tools._check_availability,
                description="Verifica si el usuario tiene disponibilidad para una fecha específica. Recibe un string en formato RFC3339, por ejemplo '2025-04-02T12:00:00+02:00'.",
                args_schema=AvailabilityInput
            ),
            Tool(
                name="FetchEvents",
                func=self.calendar_tools.fetch_events,
                description="Obtiene los próximos eventos del calendario del usuario."
            ),
            StructuredTool(
                name="GenerateEvent",
                func=lambda **kwargs: self.generate_event_tool(GenerateEventInput(**kwargs)),
                description="Genera un evento nuevo en el calendario del usuario basándose en los datos extraídos del correo.",
                args_schema=GenerateEventInput
            ),
            StructuredTool(
                name="FindEventId",
                func=self.calendar_tools.find_event_in_calendar,
                description="Busca un evento en el calendario basándose en la fecha proporcionada y devuelve su ID.",
                args_schema=FindEventInput
            ),
            StructuredTool(
                name="ChangeEvent",
                func=lambda **kwargs: self.change_event_tool(ChangeEventInput(**kwargs)),
                description="Cambia la hora de un evento existente en el calendario del usuario.",
                args_schema=ChangeEventInput
            ),
            StructuredTool(
                name="CancelEvent",
                func=lambda **kwargs: self.calendar_tools.cancel_event(kwargs["event_id"]),
                description="Cancela un evento en el calendario del usuario.",
                args_schema=CancelEventInput
            )

        ]
    
    # AFINAR EL PROMPT

    def get_prompt(self) -> PromptTemplate:
        return PromptTemplate.from_template("""
            Eres un agente experto en gestión de correos y calendarios.

            Tu tarea es:
            - Leer el contenido del correo (email_data).
            - Detectar qué acción requiere el remitente:
                * Si el correo solicita crear un nuevo evento, extrae e infiere la información necesaria y genera un objeto JSON plano con los siguientes campos:
                    - date: Fecha y hora de inicio en formato ISO 8601. Ejemplo: "2025-04-02T12:00:00+02:00".
                    - duration: Duración del evento, por ejemplo "1 hour" o "30 minutes".
                    - participants: Lista de emails de los participantes (asegúrate de incluir al remitente).
                    - event_type: Tipo de evento (por defecto "Meeting").
                    - place: Ubicación física del evento.
                    - meeting_link: Enlace a la reunión virtual si aplica.
                    - priority: Prioridad del evento, por ejemplo "Alta", "Media" o "Baja".
                    - attachments: Enlaces a archivos relacionados.
                    - deadline: Fecha límite en formato ISO 8601.
                    - details: Información adicional sobre el evento.
                Luego, invoca la tool GenerateEvent para crear el evento.
                * Si el correo solicita cambiar la fecha o el horario de un evento existente (por ejemplo, "cambiar la reunión de mañana de las 9 a las 12"), haz lo siguiente:
                    - Llama primero a la herramienta FindEventId pasando la fecha actual del evento (según lo indicado en el correo).
                    - Luego, utiliza la herramienta ChangeEvent con el event_id obtenido, la nueva fecha y, si aplica, la duración.
            - Finalmente, siempre termina invocando la tool SendEmailResponse para enviar una respuesta al remitente utilizando el email_data original.

            Usa solamente las tools disponibles.
            Nunca escribas "Final Answer".

            Si trabajas con fechas, usa la zona horaria de Madrid/España.
            Para obtener el event_id en herramientas como CancelEvent o ChangeEvent, asegúrate de haber ejecutado previamente la tool FindEventId.

            Si te piden, por ejemplo, una reunión a las 9 de la mañana, conviértelo a formato RFC3339 (ejemplo: "2025-04-02T09:00:00+02:00"). 
            Es posible que en el mensaje solo se mencione la hora; usa el contexto (fecha actual y correos anteriores) para determinar la fecha y hora correctas.

            email_data:
            {input}
        """)


    def get_llm(self):
        return self.llm
