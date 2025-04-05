import React from 'react';
import BrandSettingsForm from '../components/settings/BrandSettings';

const BrandSettingsPage: React.FC = () => {
  return (
    <div className="container mx-auto px-4 py-8">
      <h1 className="text-3xl font-bold mb-6">Brand Settings</h1>
      <p className="text-gray-600 mb-8">
        Customize your brand appearance for all generated videos. These settings will be applied by default to new videos.
      </p>
      
      <BrandSettingsForm />
    </div>
  );
};

export default BrandSettingsPage;
