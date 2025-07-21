export default function Home() {
  return (
    <main className='min-h-screen'>
      <nav className='border-b border-blue-900 p-6'>
        <div className='max-w-7xl mx-auto flex justify-between items-center'>
          <h1 className='text-2xl font-bold text-blue-400'>BlackBlue</h1>
          <div className='space-x-8'>
            <a href='#' className='text-blue-400 hover:text-blue-300 transition-colors'>Home</a>
            <a href='#' className='text-blue-400 hover:text-blue-300 transition-colors'>About</a>
            <a href='#' className='text-blue-400 hover:text-blue-300 transition-colors'>Services</a>
            <a href='#' className='text-blue-400 hover:text-blue-300 transition-colors'>Contact</a>
          </div>
        </div>
      </nav>

      <section className='py-20 px-6'>
        <div className='max-w-7xl mx-auto'>
          <div className='text-center'>
            <h2 className='text-6xl font-bold mb-6 bg-gradient-to-r from-blue-500 to-blue-300 bg-clip-text text-transparent'>
              Modern Solutions for Modern Problems
            </h2>
            <p className='text-xl text-gray-400 mb-8'>
              Transform your digital presence with our cutting-edge solutions
            </p>
            <button className='bg-blue-600 hover:bg-blue-500 text-white px-8 py-3 rounded-full transition-colors' aria-label="Button">
              Get Started
            </button>
          </div>
        </div>
      </section>

      <section className='bg-blue-900/20 py-20 px-6'>
        <div className='max-w-7xl mx-auto grid grid-cols-1 md:grid-cols-3 gap-8'>
          {[1, 2, 3].map((item) => (
            <div key={item} className='bg-black p-8 rounded-xl border border-blue-800 hover:border-blue-500 transition-colors'>
              <div className='h-12 w-12 bg-blue-500 rounded-lg mb-4'></div>
              <h3 className='text-xl font-bold mb-4 text-blue-400'>Feature {item}</h3>
              <p className='text-gray-400'>
                Experience the power of innovative technology solutions designed for the future.
              </p>
            </div>
          ))}
        </div>
      </section>

      <footer className='border-t border-blue-900 py-12 px-6'>
        <div className='max-w-7xl mx-auto text-center text-gray-400'>
          <p>&copy; 2024 BlackBlue. All rights reserved.</p>
        </div>
      </footer>
    </main>
  )
}