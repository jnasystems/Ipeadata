import { useEffect, useState } from "react";
import { motion } from "framer-motion";
import { Typewriter } from 'react-simple-typewriter';
import { FaGithub } from "react-icons/fa";
import { HiOutlineExternalLink } from "react-icons/hi";

export default function App() {
  const [imagemExpandida, setImagemExpandida] = useState(null);

  useEffect(() => {
    document.title = "Jonas Kasakewitch | Portfólio";
  }, []);

  return (
    <div className="bg-black text-white font-sans">
      {/* HERO COM LAYOUT EM DUAS COLUNAS */}
      <section className="relative bg-black min-h-screen flex flex-col justify-center">
        <div className="max-w-7xl mx-auto px-6 py-20 grid md:grid-cols-2 items-center gap-12">
          {/* Texto à esquerda */}
          <div>
            <motion.h1
              className="text-5xl md:text-7xl font-bold leading-tight mb-6"
              initial={{ opacity: 0, y: -50 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 1 }}
            >
              <span className="text-red-500">
                <Typewriter
                  words={['Bem Vindo.', 'Welcome.']}
                  loop={0}
                  cursor
                  cursorStyle="|"
                  typeSpeed={80}
                  deleteSpeed={50}
                  delaySpeed={1500}
                />
              </span>
            </motion.h1>

            <motion.p
              className="text-lg md:text-2xl text-gray-300"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.5, duration: 1 }}
            >
              Sou o Jonas um profissional com mais de 10 anos de experiência em dados, especialista em pipelines, modelagem dimensional, 
              integrações com APIs e arquitetura em nuvem. Já atuei em projetos com Azure, AWS e GCP.
            </motion.p>
          </div>

          {/* Imagem com fundo brilhante radial */}
          <motion.div
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ duration: 1 }}
            className="relative flex justify-center items-center"
          >
            <div className="absolute w-[500px] h-[500px] rounded-full bg-black opacity-60 blur-3xl z-0" />
            <img
              src="/Portfolio/images/logo1.png"
              alt="Imagem de computador"
              className="relative z-10 w-[300px] md:w-[400px]"
            />
          </motion.div>
        </div>

        {/* ONDA DECORATIVA */}
        <div className="absolute bottom-0 w-full overflow-hidden leading-none">
          <svg viewBox="0 0 1440 120" xmlns="http://www.w3.org/2000/svg">
            <path fill="#0c1a33" d="M0,0 C360,100 1080,100 1440,0 L1440,120 L0,120 Z" />
          </svg>
        </div>
      </section>

      {/* PROJETOS */}
      <section className="px-6 py-20" style={{ backgroundColor: "#0c1a33" }}>
        <h2 className="text-4xl font-bold mb-12 text-white text-center relative inline-block before:absolute before:left-0 before:top-2 before:w-1 before:h-full before:bg-red-500 pl-4">
          Projetos
        </h2>

        <div className="grid gap-8 sm:grid-cols-1 md:grid-cols-2 lg:grid-cols-3">
          {/* CARD 1 */}
          <motion.div className="bg-white rounded-2xl shadow-md hover:shadow-lg transition-all overflow-hidden" whileHover={{ scale: 1.02 }}>
            <img src="/Portfolio/images/projeto1.jpg" alt="Dashboard BI" className="w-full h-48 object-cover" onClick={() => setImagemExpandida('/Portfolio/images/projeto1.jpg')} />
            <div className="p-6">
              <h3 className="text-2xl font-semibold text-black mb-2">CryptoPrice Dashboard</h3>
              <p className="text-gray-700 mb-4">
                Dashboard interativo para acompanhar em tempo real a performance das 10 principais criptomoedas, com gráficos dinâmicos, rankings e análises visuais de mercado.
              </p>
              <div className="flex gap-4">
                <a href="https://github.com/NathanThomaz/CryptoPrice-Dashboard" target="_blank" rel="noopener noreferrer"><FaGithub className="w-6 h-6 text-black hover:text-gray-700" /></a>
                <a href="https://dashcrypto-app.streamlit.app/" target="_blank" rel="noopener noreferrer"><HiOutlineExternalLink className="w-6 h-6 text-black hover:text-gray-700" /></a>
              </div>
            </div>
          </motion.div>

          {/* CARD 2 */}
          <motion.div className="bg-white rounded-2xl shadow-md hover:shadow-lg transition-all overflow-hidden" whileHover={{ scale: 1.02 }}>
            <img src="/Portfolio/images/projeto2.png" alt="ETL Databricks" className="w-full h-48 object-cover" onClick={() => setImagemExpandida('/Portfolio/images/projeto2.png')} />
            <div className="p-6">
              <h3 className="text-2xl font-semibold text-black mb-2">Pipeline ETL com Databricks</h3>
              <p className="text-gray-700 mb-4">
                Processo automatizado com PySpark, particionamento Delta Lake e carga em camada Silver.
              </p>
              <div className="flex gap-4">
                <a href="https://github.com/seuusuario/projeto2" target="_blank" rel="noopener noreferrer"><FaGithub className="w-6 h-6 text-black hover:text-gray-700" /></a>
                <a href="https://seudominio.com/etl" target="_blank" rel="noopener noreferrer"><HiOutlineExternalLink className="w-6 h-6 text-black hover:text-gray-700" /></a>
              </div>
            </div>
          </motion.div>

          {/* CARD 3 */}
          <motion.div className="bg-white rounded-2xl shadow-md hover:shadow-lg transition-all overflow-hidden" whileHover={{ scale: 1.02 }}>
            <img src="/Portfolio/images/projeto3.jpg" alt="Integração APIs" className="w-full h-48 object-cover" onClick={() => setImagemExpandida('/Portfolio/images/projeto3.jpg')} />
            <div className="p-6">
              <h3 className="text-2xl font-semibold text-black mb-2">Integração com APIs REST</h3>
              <p className="text-gray-700 mb-4">
                Desenvolvimento de pipelines com chamadas REST automatizadas, autenticação via token e orquestração com Airflow.
              </p>
              <div className="flex gap-4">
                <a href="https://github.com/seuusuario/projeto3" target="_blank" rel="noopener noreferrer"><FaGithub className="w-6 h-6 text-black hover:text-gray-700" /></a>
                <a href="https://seudominio.com/apis" target="_blank" rel="noopener noreferrer"><HiOutlineExternalLink className="w-6 h-6 text-black hover:text-gray-700" /></a>
              </div>
            </div>
          </motion.div>

          {/* CARD 4 */}
          <motion.div className="bg-white rounded-2xl shadow-md hover:shadow-lg transition-all overflow-hidden" whileHover={{ scale: 1.02 }}>
            <img src="/Portfolio/images/projeto3.jpg" alt="Integração APIs 2" className="w-full h-48 object-cover" onClick={() => setImagemExpandida('/Portfolio/images/projeto3.jpg')} />
            <div className="p-6">
              <h3 className="text-2xl font-semibold text-black mb-2">Integração com APIs REST</h3>
              <p className="text-gray-700 mb-4">
                Desenvolvimento de pipelines com chamadas REST automatizadas, autenticação via token e orquestração com Airflow.
              </p>
              <div className="flex gap-4">
                <a href="https://github.com/seuusuario/projeto4" target="_blank" rel="noopener noreferrer"><FaGithub className="w-6 h-6 text-black hover:text-gray-700" /></a>
                <a href="https://seudominio.com/api2" target="_blank" rel="noopener noreferrer"><HiOutlineExternalLink className="w-6 h-6 text-black hover:text-gray-700" /></a>
              </div>
            </div>
          </motion.div>
        </div>
      </section>

      {/* Imagem expandida */}
      {imagemExpandida && (
        <div className="fixed inset-0 bg-black bg-opacity-80 flex items-center justify-center z-50" onClick={() => setImagemExpandida(null)}>
          <img src={imagemExpandida} alt="Imagem expandida" className="max-w-full max-h-[90vh] rounded-lg shadow-xl" onClick={(e) => e.stopPropagation()} />
        </div>
      )}

      {/* ONDA DECORATIVA INVERTIDA */}
      <div className="w-full overflow-hidden leading-none rotate-180">
        <svg viewBox="0 0 1440 120" xmlns="http://www.w3.org/2000/svg">
          <path fill="#0c1a33" d="M0,0 C360,100 1080,100 1440,0 L1440,120 L0,120 Z" />
        </svg>
      </div>

      <footer className="text-center py-10 bg-black text-gray-500">
        <motion.p initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ duration: 1 }}>
          © {new Date().getFullYear()} Jonas Kasakewitch. Todos os direitos reservados.
        </motion.p>
      </footer>
    </div>
  );
}
