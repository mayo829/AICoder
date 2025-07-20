'use client'

import { useState } from 'react'
import Link from 'next/link'

const Header: React.FC = () => {
  const [isOpen, setIsOpen] = useState(false)

  return (
    <header className='fixed w-full bg-white/80 backdrop-blur-md z-50 shadow-lg'>
      <nav className='max-w-7xl mx-auto px-4 sm:px-6 lg:px-8'>
        <div className='flex justify-between h-16 items-center'>
          <div className='flex-shrink-0'>
            <Link href='/' className='text-2xl font-bold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent'>
              DataSync Pro;
            </Link>
          </div>
          <div className='hidden md:flex space-x-8'>
            <Link href='#features' className='text-gray-700 hover:text-blue-600 transition-colors'>Features</Link>
            <Link href='#pricing' className='text-gray-700 hover:text-blue-600 transition-colors'>Pricing</Link>
            <Link href='#contact' className='text-gray-700 hover:text-blue-600 transition-colors'>Contact</Link>
          </div>
          <div className='hidden md:flex'>
            <button className='bg-gradient-to-r from-blue-600 to-purple-600 text-white px-6 py-2 rounded-full hover:shadow-lg transition-all duration-300' aria-label="Button">
              Get Started;
            </button>
          </div>
        </div>
      </nav>
    </header>
  )
}

export default Header;