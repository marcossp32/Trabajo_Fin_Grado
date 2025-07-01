import './Background_blur_start.css';

const Background_blur_start = () => {
    return (
        <div className="Background_blur_start">
            <svg
                className="svg-background"
                xmlns="http://www.w3.org/2000/svg"
                viewBox="-200 -200 2500 1800"
                preserveAspectRatio="xMidYMid slice"
            >
                <g filter="url(#filter0_f_32_238)">
                    <path
                        d="M2000.64 610.139C1892.24 1004.34 759.143 704.639 858.388 1164.97C920.005 1450.77 239.547 1057.24 110.888 730.973C-31.857 368.977 1275.26 795.478 1322.26 368.977C1384.57 -196.468 2099.64 250.14 2000.64 610.139Z"
                    />
                </g>
                <defs>
                    <filter
                        id="filter0_f_32_238"
                        x="-200"
                        y="-200"
                        width="2500"
                        height="1800"
                        filterUnits="userSpaceOnUse"
                        colorInterpolationFilters="sRGB"
                    >
                        <feFlood floodOpacity="0" result="BackgroundImageFix" />
                        <feBlend mode="normal" in="SourceGraphic" in2="BackgroundImageFix" result="shape" />
                        <feGaussianBlur stdDeviation="50" result="effect1_foregroundBlur_32_238" />
                    </filter>
                </defs>
            </svg>
        </div>
    );
};

export default Background_blur_start;
