import { useNavigate } from 'react-router';
import logo from '../assets/images/logo.png';
import oldWoman from '../assets/images/old.jpg';

export default function HomePage() {
  const navigate = useNavigate();

  return (
    <div 
      className="min-h-screen flex flex-col items-center justify-center text-white relative bg-gradient-to-br from-blue-700 to-cyan-500"
      style={{
        backgroundImage: `url(${oldWoman})`,
        backgroundSize: 'cover',
        backgroundPosition: 'center',
      }}
    >
      <div className="absolute inset-0 bg-gradient-to-br from-blue-900/80 to-cyan-700/60 z-0"></div>

      <div className="relative z-10 flex flex-col items-center">
        <div className="flex justify-center mb-6 animate-fade-in animation-delay-1000">
          <img src={logo} alt="RemediCall Logo" className="h-32 w-32 object-contain drop-shadow-lg animate-float-bounce" />
        </div>

        <h1 className="text-5xl font-extrabold mb-4 drop-shadow-md animate-fade-in animation-delay-2000">
          RemediCall
        </h1>

        <p className="text-md mb-8 italic animate-fade-in animation-delay-4000">
          Helping you never miss a dose, even when you forget.
        </p>

        <button 
          className="bg-white text-blue-700 font-bold py-3 px-8 rounded-xl text-lg transition-all shadow-lg transform hover:scale-110 hover:shadow-xl duration-300 animate-fade-in animation-delay-5000"
          onClick={() => navigate('/login')}
        >
          Get Started
        </button>
      </div>
    </div>
  );
}
