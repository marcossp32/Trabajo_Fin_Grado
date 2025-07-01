import './Background_blur_config.css';

const Background_blur_config = () => {
    return (
        <div className="background_blur_config">
            <svg
                className="svg-background-config"
                xmlns="http://www.w3.org/2000/svg"
                viewBox="0 0 2215 1256"
                preserveAspectRatio="xMidYMid slice"
            >
                <g filter="url(#filter0_f_42_990)" >
                    <path
                        d="M2104.73 623.044C1996.32 1017.25 763.374 596.71 862.619 1057.04C924.236 1342.85 243.777 949.315 115.119 623.043C-27.6266 261.048 879.569 -83.8799 1190.73 211.571C1547.23 550.071 2203.73 263.044 2104.73 623.044Z"
                        fillOpacity="0.5"
                    />
                </g>
                <defs>
                    <filter
                        id="filter0_f_42_990"
                        x="0"
                        y="-0.00012207"
                        width="2214.78"
                        height="1255.77"
                        filterUnits="userSpaceOnUse"
                        colorInterpolationFilters="sRGB"
                    >
                        <feFlood floodOpacity="0" result="BackgroundImageFix" />
                        <feBlend mode="normal" in="SourceGraphic" in2="BackgroundImageFix" result="shape" />
                        <feGaussianBlur stdDeviation="50" result="effect1_foregroundBlur_42_990" />
                    </filter>
                </defs>
            </svg>
        </div>
    );
};

export default Background_blur_config;
