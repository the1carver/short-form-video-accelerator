import React, { useState, useEffect } from 'react';
import api from '../../lib/api';
import { showSuccess, showError } from '../../components/ui/toast-utils';
import { Template } from '../../types';

interface BrandSettings {
  primaryColor: string;
  logo: string | null;
  defaultTemplateId: string | null;
  defaultCaptionStyle: {
    font_family: string;
    font_size: number;
    font_color: string;
    background_color: string;
  };
}

const BrandSettingsForm: React.FC = () => {
  const [settings, setSettings] = useState<BrandSettings>({
    primaryColor: '#3B82F6',
    logo: null,
    defaultTemplateId: null,
    defaultCaptionStyle: {
      font_family: 'Inter',
      font_size: 24,
      font_color: '#FFFFFF',
      background_color: '#000000B3'
    }
  });
  const [logoFile, setLogoFile] = useState<File | null>(null);
  const [templates, setTemplates] = useState<Template[]>([]);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  
  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);
        
        const templatesResponse = await api.endpoints.content.getTemplates();
        setTemplates(templatesResponse?.data || []);
        
        const profileResponse = await api.endpoints.user.getProfile();
        
        if (profileResponse?.data?.brandSettings) {
          setSettings(profileResponse.data.brandSettings);
        }
      } catch (error) {
        console.error('Error fetching brand settings:', error);
        showError('Failed to load brand settings');
      } finally {
        setLoading(false);
      }
    };
    
    fetchData();
  }, []);
  
  const handleLogoChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      setLogoFile(e.target.files[0]);
      
      const reader = new FileReader();
      reader.onload = (event) => {
        if (event.target && event.target.result) {
          setSettings({
            ...settings,
            logo: event.target.result as string
          });
        }
      };
      reader.readAsDataURL(e.target.files[0]);
    }
  };
  
  const handleSave = async () => {
    try {
      setSaving(true);
      
      if (logoFile) {
        const formData = new FormData();
        formData.append('file', logoFile);
        formData.append('type', 'logo');
        
        const uploadResponse = await api.endpoints.user.uploadBrandAsset(formData);
        
        if (uploadResponse?.data?.url) {
          settings.logo = uploadResponse.data.url;
        }
      }
      
      await api.endpoints.user.updateProfile({
        preferences: {
          brandSettings: settings
        }
      });
      
      showSuccess('Brand settings saved successfully');
    } catch (error) {
      console.error('Error saving brand settings:', error);
      showError('Failed to save brand settings');
    } finally {
      setSaving(false);
    }
  };
  
  if (loading) {
    return (
      <div className="flex justify-center py-8">
        <div className="animate-spin rounded-full h-8 w-8 border-t-2 border-b-2 border-blue-500"></div>
      </div>
    );
  }
  
  return (
    <div className="bg-white rounded-lg shadow overflow-hidden">
      <div className="p-6 border-b">
        <h2 className="text-xl font-semibold">Brand Settings</h2>
        <p className="text-gray-600 text-sm mt-1">
          Customize your brand appearance for all generated videos.
        </p>
      </div>
      
      <div className="p-6 space-y-6">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Brand Logo
          </label>
          <div className="flex items-center space-x-4">
            <div className="w-24 h-24 border rounded-lg flex items-center justify-center overflow-hidden bg-gray-100">
              {settings.logo ? (
                <img src={settings.logo} alt="Brand logo" className="max-w-full max-h-full" />
              ) : (
                <span className="text-gray-400">No logo</span>
              )}
            </div>
            <div>
              <input
                type="file"
                id="logo-upload"
                accept="image/*"
                className="hidden"
                onChange={handleLogoChange}
              />
              <label
                htmlFor="logo-upload"
                className="px-4 py-2 bg-gray-200 text-gray-700 rounded hover:bg-gray-300 cursor-pointer inline-block"
              >
                Upload Logo
              </label>
              <p className="text-xs text-gray-500 mt-1">
                Recommended size: 512x512px, PNG or JPG
              </p>
            </div>
          </div>
        </div>
        
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Primary Brand Color
          </label>
          <div className="flex items-center space-x-2">
            <input
              type="color"
              value={settings.primaryColor}
              onChange={(e) => setSettings({...settings, primaryColor: e.target.value})}
              className="w-10 h-10 rounded border p-0"
            />
            <input
              type="text"
              value={settings.primaryColor}
              onChange={(e) => setSettings({...settings, primaryColor: e.target.value})}
              className="px-3 py-2 border rounded-md w-32"
            />
          </div>
        </div>
        
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Default Template
          </label>
          <select
            value={settings.defaultTemplateId || ''}
            onChange={(e) => setSettings({...settings, defaultTemplateId: e.target.value || null})}
            className="w-full px-3 py-2 border rounded-md"
          >
            <option value="">No default template</option>
            {templates.map((template) => (
              <option key={template.id} value={template.id}>
                {template.name}
              </option>
            ))}
          </select>
        </div>
        
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Default Caption Style
          </label>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-xs text-gray-500 mb-1">Font Family</label>
              <select
                value={settings.defaultCaptionStyle.font_family}
                onChange={(e) => setSettings({
                  ...settings,
                  defaultCaptionStyle: {
                    ...settings.defaultCaptionStyle,
                    font_family: e.target.value
                  }
                })}
                className="w-full px-3 py-2 border rounded-md"
              >
                <option value="Inter">Inter</option>
                <option value="Roboto">Roboto</option>
                <option value="Montserrat">Montserrat</option>
                <option value="Open Sans">Open Sans</option>
              </select>
            </div>
            
            <div>
              <label className="block text-xs text-gray-500 mb-1">Font Size</label>
              <input
                type="number"
                min="12"
                max="48"
                value={settings.defaultCaptionStyle.font_size}
                onChange={(e) => setSettings({
                  ...settings,
                  defaultCaptionStyle: {
                    ...settings.defaultCaptionStyle,
                    font_size: parseInt(e.target.value)
                  }
                })}
                className="w-full px-3 py-2 border rounded-md"
              />
            </div>
            
            <div>
              <label className="block text-xs text-gray-500 mb-1">Font Color</label>
              <div className="flex items-center space-x-2">
                <input
                  type="color"
                  value={settings.defaultCaptionStyle.font_color}
                  onChange={(e) => setSettings({
                    ...settings,
                    defaultCaptionStyle: {
                      ...settings.defaultCaptionStyle,
                      font_color: e.target.value
                    }
                  })}
                  className="w-8 h-8 rounded border p-0"
                />
                <input
                  type="text"
                  value={settings.defaultCaptionStyle.font_color}
                  onChange={(e) => setSettings({
                    ...settings,
                    defaultCaptionStyle: {
                      ...settings.defaultCaptionStyle,
                      font_color: e.target.value
                    }
                  })}
                  className="px-3 py-2 border rounded-md flex-1"
                />
              </div>
            </div>
            
            <div>
              <label className="block text-xs text-gray-500 mb-1">Background Color</label>
              <div className="flex items-center space-x-2">
                <input
                  type="color"
                  value={settings.defaultCaptionStyle.background_color}
                  onChange={(e) => setSettings({
                    ...settings,
                    defaultCaptionStyle: {
                      ...settings.defaultCaptionStyle,
                      background_color: e.target.value
                    }
                  })}
                  className="w-8 h-8 rounded border p-0"
                />
                <input
                  type="text"
                  value={settings.defaultCaptionStyle.background_color}
                  onChange={(e) => setSettings({
                    ...settings,
                    defaultCaptionStyle: {
                      ...settings.defaultCaptionStyle,
                      background_color: e.target.value
                    }
                  })}
                  className="px-3 py-2 border rounded-md flex-1"
                />
              </div>
            </div>
          </div>
        </div>
      </div>
      
      <div className="p-6 border-t bg-gray-50">
        <button
          onClick={handleSave}
          disabled={saving}
          className={`px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 transition-colors ${
            saving ? 'opacity-50 cursor-not-allowed' : ''
          }`}
        >
          {saving ? 'Saving...' : 'Save Brand Settings'}
        </button>
      </div>
    </div>
  );
};

export default BrandSettingsForm;
