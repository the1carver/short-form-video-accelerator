import React from 'react';
import { Outlet } from 'react-router-dom';
import Header from './Header';

const MainLayout: React.FC = () => {
  return (
    <div className="min-h-screen bg-gray-50">
      <Header />
      <main className="pb-12">
        <Outlet />
      </main>
      <footer className="bg-white shadow-inner py-4 mt-auto">
        <div className="container mx-auto px-4">
          <p className="text-center text-gray-500 text-sm">
            &copy; {new Date().getFullYear()} Digital Frontier Short-Form Video Accelerator
          </p>
        </div>
      </footer>
    </div>
  );
};

export default MainLayout;
