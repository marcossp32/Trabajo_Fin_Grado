import './Info.css';
import { useEffect } from 'react';


const Info = () => {
    const getSafeTheme = () => {
    const theme = localStorage.getItem('theme');
    if (theme === "dark" || theme === "light") return theme;
    return window.matchMedia('(prefers-color-scheme: dark)').matches ? "dark" : "light";
  };

  useEffect(() => {
    const theme = getSafeTheme();
    document.documentElement.setAttribute('data-theme', theme);
  }, []);

  return (

    <section className="info-section">
    <a href="/"><h1>AISERV</h1></a>
    <div className="info-container">
      {/* ──────────────── CONTACTO ──────────────── */}
      <div id="contact" className="info-block">
        <h2>Contacto</h2>
        <p>
          Correo electrónico:&nbsp;
          <a href="mailto:info@aiserv.es" aria-label="Enviar correo a AISERV">
            aiserv.soporte@gmail.com
          </a>
        </p>
      </div>

      {/* ────────── TÉRMINOS DE USO ────────── */}
        <div id="terms" className="info-block">
            <h2>Términos de uso</h2>

            {/* 1. Información del prestador */}
            <h3>1. Información del prestador</h3>
            <p>
                En cumplimiento del artículo 10 de la Ley 34/2002, de 11 de julio, de Servicios
                de la Sociedad de la Información y de Comercio Electrónico (LSSI-CE), se informa
                que el sitio web AISERV es un proyecto personal sin ánimo de lucro ni forma
                jurídica constituida.
            </p>
            {/* 2. Objeto y ámbito de aplicación */}
            <h3>2. Objeto y ámbito de aplicación</h3>
            <p>
                Estas Condiciones regulan el acceso y uso del sitio web AISERV (en adelante,
                el «Sitio») y de todos los servicios digitales que el prestador pone a disposición
                de los usuarios.

                AISERV permite a los usuarios autenticarse únicamente mediante el sistema
                OAuth2 de Google, accediendo sólo a los permisos concedidos por el propio usuario
                para la lectura, creación y eliminación de correos electrónicos y eventos de
                calendario a través de las APIs de Google.
            </p>

            {/* 3. Aceptación de las condiciones */}
            <h3>3. Aceptación de las condiciones</h3>
            <p>
                Al iniciar sesión mediante el sistema OAuth2, el usuario declara haber leído,
                comprendido y aceptado íntegramente estas Condiciones. Asimismo, acepta
                expresamente los riesgos inherentes al uso de servicios digitales, como fallos
                técnicos, ciberataques, pérdida de datos o interrupciones del servicio.

                Nada de lo dispuesto limita o excluye la responsabilidad que no pueda ser
                legalmente limitada, especialmente la derivada de dolo o negligencia grave, ni
                los derechos reconocidos a los consumidores por la legislación vigente.
            </p>

            {/* 4. Registro y acceso a la cuenta */}
            <h3>4. Registro y acceso a la cuenta</h3>
            <p>
                El acceso a las funcionalidades se realiza exclusivamente mediante inicio de
                sesión con Google. AISERV sólo accederá a los permisos autorizados por el
                usuario, sin almacenar contraseñas ni credenciales.

                El usuario es responsable del uso de su cuenta de Google. En caso de uso no
                autorizado, deberá revocar el acceso desde su panel de seguridad de Google.

                El prestador podrá suspender el acceso si detecta usos contrarios a estas
                Condiciones o a la normativa aplicable.
            </p>

            {/* 5. Obligaciones del usuario */}
            <h3>5. Obligaciones del usuario</h3>
            <p>
                Utilizar el Sitio conforme a la ley, la moral y el orden público.
                No realizar actividades ilícitas, actos de intrusión o accesos no autorizados.
                No introducir ni difundir contenidos que lesionen derechos de terceros o contengan virus informáticos.
                Indemnizar al prestador por cualquier daño o perjuicio derivado del incumplimiento de estas obligaciones.
            </p>

            {/* 6. Propiedad intelectual e industrial */}
            <h3>6. Propiedad intelectual e industrial</h3>
            <p>
                Todos los derechos de propiedad intelectual e industrial sobre el Sitio, su diseño,
                códigos fuente y contenidos (textos, imágenes, vídeos, software, etc.) pertenecen
                al prestador o cuenta con licencias legítimas. Algunos iconos o recursos visuales
                utilizados en el Sitio pueden proceder de bancos de recursos de libre uso o con
                licencia para uso personal y/o comercial. En dichos casos, se respetan los
                términos de licencia aplicables de sus respectivos autores.

                Queda prohibida su reproducción, distribución o comunicación pública fuera de los
                supuestos legalmente previstos o sin autorización expresa.
            </p>

            {/* 7. Protección de datos personales */}
            <h3>7. Protección de datos personales</h3>
            <p>
                El tratamiento de datos personales se rige por el Reglamento (UE) 2016/679
                (RGPD) y la Ley Orgánica 3/2018, de 5 de diciembre (LOPDGDD). La información
                completa sobre finalidades, legitimación, destinatarios y derechos se recoge en
                la Política de Privacidad.
            </p>

            {/* 8. Exclusión de garantías */}
            <h3>8. Exclusión de garantías</h3>
            <p>
                El Sitio se presta «tal cual» y según disponibilidad. No se garantiza la continuidad
                del servicio ni la ausencia de errores, virus u otros componentes dañinos. El
                usuario asume la plena responsabilidad del uso del Sitio.
            </p>

            {/* 9. Limitación de responsabilidad */}
            <h3>9. Limitación de responsabilidad</h3>
            <p>
                El prestador solo responderá de los daños causados por dolo o negligencia grave.
                En ningún caso será responsable de:
            
                Pérdidas de negocio, lucro cesante o daños indirectos.
                Contenidos de terceros o errores en los datos obtenidos vía APIs.


                En todo caso, la responsabilidad quedará limitada a los márgenes permitidos por
                la legislación vigente.
            </p>

            {/* 10. Enlaces externos */}
            <h3>10. Enlaces externos</h3>
            <p>
                El Sitio puede incluir enlaces a sitios de terceros. El prestador no ejerce control
                alguno sobre dichos sitios ni se responsabiliza de sus contenidos o seguridad.
            </p>

            {/* 11. Suspensión y cancelación de servicios */}
            <h3>11. Suspensión y cancelación de servicios</h3>
            <p>
                El prestador podrá suspender temporal o definitivamente el Sitio sin necesidad de
                notificación previa, cuando lo considere oportuno o por causas de fuerza mayor.
            </p>

            {/* 12. Modificaciones */}
            <h3>12. Modificaciones</h3>
            <p>
                El prestador podrá modificar estas Condiciones en cualquier momento. Las nuevas
                versiones se publicarán en el Sitio y serán vinculantes desde su publicación. Se
                considerará que el usuario acepta los cambios si accede al Sitio tras la
                actualización.
            </p>

            {/* 13. Legislación aplicable y jurisdicción */}
            <h3>13. Legislación aplicable y jurisdicción</h3>
            <p>
                Estas Condiciones se rigen por la legislación española. Las partes se someten,
                con renuncia expresa a cualquier otro fuero, a los Juzgados y Tribunales que
                resulten competentes conforme a la normativa vigente.
            </p>
        </div>


      {/* ────────── POLÍTICA DE PRIVACIDAD ────────── */}
        <div id="privacy" className="info-block">
            <h2>Política de privacidad</h2>

            <h3>1. Responsable del tratamiento</h3>
            <p>
                De conformidad con el Reglamento (UE) 2016/679 (RGPD) y la Ley Orgánica 3/2018, de 5 de diciembre (LOPDGDD), 
                se informa que el responsable del tratamiento de los datos personales recogidos a través del sitio web AISERV 
                (en adelante, el «Sitio» o «AISERV») es AISERV, un proyecto personal sin ánimo de lucro ni forma jurídica constituida.
                 El correo electrónico de contacto es aiserv.soporte@gmail.com.
            </p>

            <h3>2. Datos tratados</h3>
            <p>
                Al utilizar AISERV pueden tratarse datos de autenticación de Google como identificador de usuario (ID), token OAuth2 y,
                 en su caso, dirección de correo electrónico; metadatos de correos electrónicos como remitente, destinatario(s), asunto,
                  fecha/hora y etiquetas; contenido de correos electrónicos y archivos adjuntos solo cuando el usuario lo autorice expresamente 
                  mediante los permisos de Gmail API; eventos de Google Calendar como título, descripción, ubicación, participantes y fecha/hora; 
                  y datos de uso como registros técnicos sobre actividad, errores y estadísticas de rendimiento. AISERV no solicita ni almacena 
                  contraseñas de Google ni otros datos sensibles no comprendidos dentro de los permisos otorgados.
            </p>

            <h3>3. Finalidad y base jurídica</h3>
            <p>
                Los datos se tratan para proporcionar las funcionalidades principales de AISERV con base en el consentimiento del usuario mediante OAuth2;
                 para gestionar incidencias y mantener la seguridad con base en el interés legítimo del responsable; para atender derechos ARSOPOL y 
                 consultas en cumplimiento de obligaciones legales; y para responder a requerimientos legales también por obligación normativa. ARSOPOL 
                 incluye los derechos de Acceso, Rectificación, Supresión (Derecho al olvido), Portabilidad, Oposición y Limitación.
            </p>

            <h3>4. Destinatarios</h3>
            <p>
                Los datos podrán ser tratados por Google LLC en calidad de encargado del tratamiento para la prestación de los servicios de API,
                 por proveedores de hosting en la UE y por autoridades competentes cuando exista obligación legal. No se cederán datos a terceros
                  distintos salvo obligación legal o consentimiento expreso.
            </p>

            <h3>5. Transferencias internacionales</h3>
            <p>
                Cuando Google LLC procese datos fuera del Espacio Económico Europeo, aplicará las cláusulas contractuales tipo aprobadas por la 
                Comisión Europea y medidas complementarias que garanticen un nivel de protección equivalente al europeo.
            </p>

            <h3>6. Plazo de conservación</h3>
            <p>
                Los datos se conservarán mientras el usuario mantenga activa su cuenta y no revoque los permisos de Google, mientras 
                resulten necesarios para las finalidades descritas o exista una obligación legal. Una vez cumplidos estos plazos, se 
                bloquearán y eliminarán de forma segura.
            </p>

            <h3>7. Derechos de las personas interesadas</h3>
            <p>
                El usuario puede ejercer sus derechos de acceso, rectificación, supresión, portabilidad, limitación y oposición escribiendo 
                a aiserv.soporte@gmail.com con el asunto «Ejercicio de derechos RGPD» y acreditando su identidad. También puede revocar los 
                permisos desde la Consola de Seguridad de Google. Asimismo, puede presentar una reclamación ante la Agencia Española de 
                Protección de Datos si considera que el tratamiento no cumple la normativa.
            </p>

            <h3>8. Medidas de seguridad</h3>
            <p>
                AISERV aplica medidas técnicas y organizativas apropiadas como el cifrado de los tokens OAuth2, el registro de accesos y errores, 
                el uso de conexiones HTTPS/TLS y un control de acceso basado en privilegios mínimos para garantizar la confidencialidad, integridad 
                y disponibilidad de los datos.
            </p>

            <h3>9. Actualizaciones de la política</h3>
            <p>
                AISERV podrá modificar esta Política de Privacidad para adaptarla a cambios legales o nuevas funcionalidades. 
                Las versiones actualizadas se publicarán en el Sitio con indicación de la fecha de revisión.
            </p>
        </div>



      {/* ────────── AVISO FINAL ────────── */}
      <div className="info-accept">
        <p>
          El uso de AISERV presupone la
          aceptación de todas las políticas y condiciones anteriores. Última
          actualización: <time dateTime="2025-06-11">11 jun 2025</time>.
        </p>
      </div>
    </div>
  </section>

  )
  
}

export default Info;
