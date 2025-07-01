
import './Footer.css'

const Footer = () =>{

    return(
        <footer>

            <div className="footer-text">
                
                <h2>AISERV</h2>
                <p>Empowering your meeting management with automation and AI.</p>
            
            </div>
            <div className="footer-bottom">
                <a href="/">Home</a>
                <a href="/info">Terms</a>
                <p>&copy; 2024 AISERV All Rights Reserved.</p>
                <a href="/info">Credits</a>
                <a href="/info">Contact</a>
            </div>  

        </footer>
    )
}

export default Footer