import React, { useState, useEffect } from 'react';
import api from '../lib/api';
import { showError } from '../components/ui/toast-utils';

interface Template {
  id: string;
  name: string;
  description: string;
  thumbnail_url: string;
  platform: string;
  category: string;
}

const TemplatesPage: React.FC = () => {
  const [templates, setTemplates] = useState<Template[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedCategory, setSelectedCategory] = useState<string>('all');
  const [selectedPlatform, setSelectedPlatform] = useState<string>('all');
  
  const categories = ['all', 'promotional', 'educational', 'entertainment', 'tutorial'];
  const platforms = ['all', 'tiktok', 'instagram', 'youtube'];
  
  useEffect(() => {
    const fetchTemplates = async () => {
      try {
        setLoading(true);
        const response = await api.endpoints.content.getTemplates();
        
        // Use mock data for development if API doesn't return data
        const mockTemplates: Template[] = [
          {
            id: '1',
            name: 'TikTok Explainer',
            description: 'Short, engaging explainer template optimized for TikTok with captions and music.',
            thumbnail_url: 'https://via.placeholder.com/300x500?text=TikTok+Explainer',
            platform: 'tiktok',
            category: 'educational'
          },
          {
            id: '2',
            name: 'Product Showcase',
            description: 'Highlight your product features with this dynamic template.',
            thumbnail_url: 'https://via.placeholder.com/300x500?text=Product+Showcase',
            platform: 'tiktok',
            category: 'promotional'
          },
          {
            id: '3',
            name: 'Tutorial Steps',
            description: 'Break down complex processes into simple steps.',
            thumbnail_url: 'https://via.placeholder.com/300x500?text=Tutorial+Steps',
            platform: 'tiktok',
            category: 'tutorial'
          },
          {
            id: '4',
            name: 'Entertainment Clip',
            description: 'Engaging template for entertainment content with dynamic transitions.',
            thumbnail_url: 'https://via.placeholder.com/300x500?text=Entertainment+Clip',
            platform: 'tiktok',
            category: 'entertainment'
          },
          {
            id: '5',
            name: 'Instagram Story',
            description: 'Vertical template optimized for Instagram stories.',
            thumbnail_url: 'https://via.placeholder.com/300x500?text=Instagram+Story',
            platform: 'instagram',
            category: 'promotional'
          },
          {
            id: '6',
            name: 'YouTube Short',
            description: 'Template designed for YouTube Shorts format.',
            thumbnail_url: 'https://via.placeholder.com/300x500?text=YouTube+Short',
            platform: 'youtube',
            category: 'entertainment'
          }
        ];
        
        setTemplates(response?.data || mockTemplates);
      } catch (error) {
        console.error('Error fetching templates:', error);
        showError('Failed to load templates. Please try again later.');
      } finally {
        setLoading(false);
      }
    };
    
    fetchTemplates();
  }, []);
  
  const filteredTemplates = templates.filter(template => {
    const matchesCategory = selectedCategory === 'all' || template.category === selectedCategory;
    const matchesPlatform = selectedPlatform === 'all' || template.platform === selectedPlatform;
    return matchesCategory && matchesPlatform;
  });
  
  return (
    <div className="container mx-auto px-4 py-8">
      <div className="flex justify-between items-center mb-8">
        <h1 className="text-3xl font-bold">Video Templates</h1>
      </div>
      
      <div className="mb-8">
        <div className="flex flex-wrap gap-4">
          <div>
            <label htmlFor="category-filter" className="block text-sm font-medium text-gray-700 mb-1">
              Category
            </label>
            <select
              id="category-filter"
              value={selectedCategory}
              onChange={(e) => setSelectedCategory(e.target.value)}
              className="block w-full pl-3 pr-10 py-2 text-base border-gray-300 focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm rounded-md"
            >
              {categories.map((category) => (
                <option key={category} value={category}>
                  {category.charAt(0).toUpperCase() + category.slice(1)}
                </option>
              ))}
            </select>
          </div>
          
          <div>
            <label htmlFor="platform-filter" className="block text-sm font-medium text-gray-700 mb-1">
              Platform
            </label>
            <select
              id="platform-filter"
              value={selectedPlatform}
              onChange={(e) => setSelectedPlatform(e.target.value)}
              className="block w-full pl-3 pr-10 py-2 text-base border-gray-300 focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm rounded-md"
            >
              {platforms.map((platform) => (
                <option key={platform} value={platform}>
                  {platform.charAt(0).toUpperCase() + platform.slice(1)}
                </option>
              ))}
            </select>
          </div>
        </div>
      </div>
      
      {loading ? (
        <div className="flex justify-center items-center h-64">
          <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-blue-500"></div>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {filteredTemplates.length > 0 ? (
            filteredTemplates.map((template) => (
              <div key={template.id} className="bg-white rounded-lg shadow overflow-hidden">
                <div className="h-80 bg-gray-200">
                  <img 
                    src={template.thumbnail_url} 
                    alt={template.name} 
                    className="w-full h-full object-cover"
                  />
                </div>
                <div className="p-4">
                  <div className="flex justify-between items-start mb-2">
                    <h3 className="text-lg font-semibold">{template.name}</h3>
                    <span className="px-2 py-1 bg-blue-100 text-blue-800 text-xs rounded-full capitalize">
                      {template.platform}
                    </span>
                  </div>
                  <p className="text-gray-600 text-sm mb-4">{template.description}</p>
                  <div className="flex justify-between items-center">
                    <span className="text-xs text-gray-500 capitalize">
                      {template.category}
                    </span>
                    <button 
                      className="px-4 py-2 bg-blue-600 text-white text-sm rounded hover:bg-blue-700 transition-colors"
                      onClick={() => {
                        // This would typically navigate to content selection or template preview
                        console.log(`Selected template: ${template.id}`);
                      }}
                    >
                      Use Template
                    </button>
                  </div>
                </div>
              </div>
            ))
          ) : (
            <div className="col-span-full text-center py-12">
              <p className="text-gray-500">No templates found matching your filters.</p>
              <button
                className="mt-4 text-blue-600 hover:text-blue-800"
                onClick={() => {
                  setSelectedCategory('all');
                  setSelectedPlatform('all');
                }}
              >
                Clear filters
              </button>
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default TemplatesPage;
