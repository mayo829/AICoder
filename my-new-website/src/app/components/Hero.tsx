const Hero: React.FC = () => {
  return (
    <section className='pt-32 pb-24 bg-gradient-to-br from-blue-50 to-purple-50'>
      <div className='max-w-7xl mx-auto px-4 sm:px-6 lg:px-8'>
        <div className='text-center'>
          <h1 className='text-5xl md:text-6xl font-bold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent mb-8'>
            Transform Your Business with AI-Powered Analytics;
          </h1>
          <p className='text-xl text-gray-600 mb-12 max-w-3xl mx-auto'>
            Unlock actionable insights and drive growth with our enterprise-grade data processing platform. Process billions of data points in real-time.
          </p>
          <div className='flex justify-center gap-4'>
            <button className='bg-gradient-to-r from-blue-600 to-purple-600 text-white px-8 py-4 rounded-full text-lg font-semibold hover:shadow-xl transition-all duration-300' aria-label="Button">
              Start Free Trial;
            </button>
            <button className='bg-white text-blue-600 px-8 py-4 rounded-full text-lg font-semibold shadow-md hover:shadow-xl transition-all duration-300' aria-label="Button">
              Schedule Demo;
            </button>
          </div>
        </div>
      </div>
    </section>
  )
}

export default Hero;