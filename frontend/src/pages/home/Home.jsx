import './Home.css'
import { useEffect, useRef, useState } from 'react'
import { useLocation } from 'react-router-dom'


import Header from '@components/header/Header'
import Footer from '@components/footer/Footer'
import Square2 from '@components/square2_personalize/Square2_personalize'
import Square3 from '@components/square3_day/Square3_day'
import Go_down from '@components/go_down/Go_down'
import Tobby_hello from '@components/tobby_hello/Tobby_hello'
import Tobby_pencil from '@components/tobby_pencil/Tobby_pencil'
import BoxContainer from '@components/box_container/Box_container'
import Start_section from '@components/start_title_section/Start_title_section'
import Tobby_point_out from '@components/tobby_point_out/Tobby_point_out'
import Background_blur_start from '@components/background_blur_start/Background_blur_start'
import Background_blur_about from '@components/background_blur_about/Background_blur_about'
import Connect from '@components/connect/Connect'

const Home = () => {
    const [activeIndex, setActiveIndex] = useState(0);
    const [AuthState, setAuthState] = useState(false);
    const [showConnect, setShowConnect] = useState(false);
    const boxesRef = useRef([]);
    const highlightRef = useRef(null);
    const [highlightClass, setHighlightClass] = useState('');
    const cursorRef = useRef(null);

    // Estado para detectar si estamos en mobile (ancho < 768px)
    const [isMobile, setIsMobile] = useState(window.innerWidth < 768);

    useEffect(() => {
        const handleResize = () => {
            setIsMobile(window.innerWidth < 768);
        };
        window.addEventListener('resize', handleResize);
        return () => window.removeEventListener('resize', handleResize);
    }, []);

    useEffect(() => {
        const handleMouseMove = (e) => {
            setTimeout(() => {
                if (cursorRef.current) {
                    const cursorSize = 10; // Tamaño del cursor
                    cursorRef.current.style.left = `${e.clientX - cursorSize / 2}px`;
                    cursorRef.current.style.top = `${e.clientY - cursorSize / 2}px`;
                }
            }, 0);
        };

        document.addEventListener('mousemove', handleMouseMove);
        return () => {
            document.removeEventListener('mousemove', handleMouseMove);
        };
    }, []);

    const boxes = [
        {
            number: "01",
            title: "COMUNICACIÓN EFECTIVA",
            description:
                "Este asistente gestiona automáticamente invitaciones, confirmaciones, dudas... asegurando que los participantes estén siempre informados y reduciendo la necesidad de seguimiento manual.",
        },
        {
            number: "02",
            title: "DISPONIBILIDAD",
            description:
                "Sincroniza horarios y prioridades para identificar los momentos más adecuados para reuniones, evitando conflictos de agenda y optimizando el tiempo de todos los involucrados.",
        },
        {
            number: "03",
            title: "AUTOMATIZACIÓN",
            description:
                "Toma decisiones automáticas, como aceptar o rechazar reuniones, basándose en criterios configurados como prioridades, horarios laborales y duración máxima permitida.",
        },
    ];

    useEffect(() => {
        const handleScroll = () => {
            let closestIndex = 0;
            let closestDistance = Infinity;

            boxesRef.current.forEach((box, index) => {
                if (box) {
                    const rect = box.getBoundingClientRect();
                    const boxCenter = rect.top + rect.height / 2;
                    const viewportCenter = window.innerHeight / 2;
                    const distance = Math.abs(viewportCenter - boxCenter);
                    if (distance < closestDistance) {
                        closestDistance = distance;
                        closestIndex = index;
                    }
                }
            });

            setActiveIndex(closestIndex);

            if (highlightRef.current) {
                const rect = highlightRef.current.getBoundingClientRect();
                const viewportHeight = window.innerHeight;
                if (rect.top < viewportHeight * 0.9 && rect.bottom > viewportHeight * 0.1) {
                    setHighlightClass('highlight-visible');
                } else {
                    setHighlightClass('');
                }
            }
        };

        window.addEventListener('scroll', handleScroll);
        return () => window.removeEventListener('scroll', handleScroll);
    }, []);

    const location = useLocation();

    useEffect(() => {
        if (location.state?.scrollTo) {
            const el = document.getElementById(location.state.scrollTo);
            if (el) {
                setTimeout(() => {
                    el.scrollIntoView({ behavior: 'smooth' });
                }, 100); // pequeña espera para que todo cargue
            }
        }
    }, [location]);

    return (
        <section className="home">
            <div ref={cursorRef} className="custom-cursor"></div>
            <Header setAuthState={setAuthState} />
            {showConnect && <Connect show={showConnect} onClose={() => setShowConnect(false)} />}
            
            <section className="start">
                <Background_blur_start />
                <Tobby_point_out />
                <Start_section AuthState={AuthState} onOpenConnect={() => setShowConnect(true)} />
            </section>

            <Go_down />

            <section className="product">
                <h2 className="product-title" id='product-title'>
                    Descubre lo que <span className={`highlight ${highlightClass}`} ref={highlightRef}>aiserv</span> puede hacer
                </h2>
                <Tobby_hello />
                {boxes.map((box, index) => (
                    <BoxContainer
                        key={index}
                        number={box.number}
                        title={box.title}
                        description={box.description}
                        isActive={index === activeIndex}
                        isOdd={index % 2 === 0}
                        ref={(el) => (boxesRef.current[index] = el)}
                    />
                ))}
            </section>

            <div className="tobby-pencil-cont" id='about-scroll'>
                <Tobby_pencil />
            </div>

            <section className="about">
                {isMobile ? (
                    <>
                        <div className="about-text">
                        <Background_blur_about />
                            <h2 className="about-title">About</h2>
                            <div className="about-me">
                                <p>
                                    Somos una empresa apasionada por la tecnología y su capacidad para mejorar nuestras vidas. AISERV nace como un proyecto personal con un objetivo claro: simplificar la gestión del tiempo y las tareas diarias utilizando herramientas inteligentes.
                                </p>
                            </div>
                            <div className="about-mision">
                                <p>
                                    Nuestra <span className="highlight">misión</span> es transformar la forma en que gestionamos el tiempo. Con AISERV, quiero crear una herramienta que no solo simplifique tu día a día, sino que te ofrezca tranquilidad y control.
                                </p>
                            </div>
                        </div>
                    </>
                ) : (
                    <>
                        {/* Orden original en escritorio */}
                        <div className="about-text">
                            <h2 className="about-title">About</h2>
                            <div className="about-me">
                                <p>
                                    Somos una empresa apasionada por la tecnología y su capacidad para mejorar nuestras vidas. AISERV nace como un proyecto personal con un objetivo claro: simplificar la gestión del tiempo y las tareas diarias utilizando herramientas inteligentes.
                                </p>
                            </div>
                            <div className="about-mision">
                                <p>
                                    Nuestra <span className="highlight">misión</span> es transformar la forma en que gestionamos el tiempo. Con AISERV, quiero crear una herramienta que no solo simplifique tu día a día, sino que te ofrezca tranquilidad y control.
                                </p>
                            </div>
                        </div>
                        <Background_blur_about />
                        <div className="about-visual">
                            <Square2 />
                            <Square3 />
                        </div>
                    </>
                )}
            </section>

            <Footer />
        </section>
    );
};

export default Home;
