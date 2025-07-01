import './Background_blur_about.css';

const Background_blur_about = () => {
    return (
        <div className="background_blur_about">
            <svg
                className="svg-background-about"
                xmlns="http://www.w3.org/2000/svg"
                viewBox="-240 -75 1737 975"
                preserveAspectRatio="xMidYMid slice"
            >
                <g filter="url(#filter0_f_32_370)" transform='scale(0.7)'>
                    <path
                        d="M1151.16 120.491C677.405 99.8266 1001.55 39.1902 356.374 311.063C3.44531 459.784 -0.446899 796.761 440.763 856.718C930.281 923.24 731.174 794.538 1290.28 690.309C1896.6 577.277 1615.26 140.735 1151.16 120.491Z"
                    />
                </g>
                <defs>
                    <filter
                        id="filter0_f_32_370"
                        x="0"
                        y="0"
                        width="1737"
                        height="975"
                        filterUnits="userSpaceOnUse"
                        colorInterpolationFilters="sRGB"
                    >
                        <feFlood floodOpacity="0" result="BackgroundImageFix" />
                        <feBlend mode="normal" in="SourceGraphic" in2="BackgroundImageFix" result="shape" />
                        <feGaussianBlur stdDeviation="50" result="effect1_foregroundBlur_32_370" />
                    </filter>
                </defs>
            </svg>
        </div>
    );
};

export default Background_blur_about;
