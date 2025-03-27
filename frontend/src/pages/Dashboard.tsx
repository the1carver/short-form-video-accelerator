import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import api from '../lib/api';

interface ContentItem {
  id: string;
  title: string;
  type: string;
  created_at: string;
  status: string;
  thumbnail_url?: string;
}

const Dashboard: React.FC = () => {
  const [recentContent, setRecentContent] = useState<ContentItem[]>([]);
  const [recentVideos, setRecentVideos] = useState<ContentItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchDashboardData = async () => {
      try {
        setLoading(true);
        
        // Fetch recent content
        const contentResponse = await api.endpoints.content.listContent({ 
          limit: 5, 
          page: 1 
        });
        
        // Simulate data for development
        const mockContent: ContentItem[] = [
          {
            id: '1',
            title: 'Marketing Presentation Q1 2025',
            type: 'presentation',
            created_at: '2025-03-24T10:30:00Z',
            status: 'analyzed',
            thumbnail_url: 'https://via.placeholder.com/300x200?text=Presentation'
          },
          {
            id: '2',
            title: 'Product Tutorial Series',
            type: 'tutorial',
            created_at: '2025-03-23T14:15:00Z',
            status: 'completed',
            thumbnail_url: 'https://via.placeholder.com/300x200?text=Tutorial'
          },
          {
            id: '3',
            title: 'Customer Interview - Enterprise Solutions',
            type: 'interview',
            created_at: '2025-03-22T09:45:00Z',
            status: 'processing',
            thumbnail_url: 'https://via.placeholder.com/300x200?text=Interview'
          }
        ];
        
        // Use real data if available, otherwise use mock data
        setRecentContent(contentResponse?.data?.items || mockContent);
        
        // Mock recent videos
        const mockVideos: ContentItem[] = [
          {
            id: '101',
            title: 'TikTok - 5 Tips for Better Engagement',
            type: 'video',
            created_at: '2025-03-24T16:20:00Z',
            status: 'published',
            thumbnail_url: 'https://via.placeholder.com/300x200?text=TikTok+Video'
          },
          {
            id: '102',
            title: 'Product Feature Highlight',
            type: 'video',
            created_at: '2025-03-23T11:30:00Z',
            status: 'published',
            thumbnail_url: 'https://via.placeholder.com/300x200?text=Feature+Video'
          }
        ];
        
        setRecentVideos(mockVideos);
        setError(null);
      } catch (err: any) {
        console.error('Error fetching dashboard data:', err);
        setError('Failed to load dashboard data. Please try again later.');
      } finally {
        setLoading(false);
      }
    };
    
    fetchDashboardData();
  }, []);

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="flex justify-between items-center mb-8">
        <h1 className="text-3xl font-bold">Dashboard</h1>
        <Link 
          to="/upload" 
          className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg flex items-center"
        >
          <span className="mr-2">+</span> Upload Content
        </Link>
      </div>
      
      {error && (
        <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-6">
          {error}
        </div>
      )}
      
      {loading ? (
        <div className="flex justify-center items-center h-64">
          <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-blue-500"></div>
        </div>
      ) : (
        <>
          {/* Quick Stats */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
            <div className="bg-white rounded-lg shadow p-6">
              <h3 className="text-lg font-semibold mb-2">Content Uploaded</h3>
              <p className="text-3xl font-bold">{recentContent.length}</p>
              <p className="text-gray-500 text-sm">Last 30 days</p>
            </div>
            <div className="bg-white rounded-lg shadow p-6">
              <h3 className="text-lg font-semibold mb-2">Videos Created</h3>
              <p className="text-3xl font-bold">{recentVideos.length}</p>
              <p className="text-gray-500 text-sm">Last 30 days</p>
            </div>
            <div className="bg-white rounded-lg shadow p-6">
              <h3 className="text-lg font-semibold mb-2">Average Engagement</h3>
              <p className="text-3xl font-bold">78%</p>
              <p className="text-gray-500 text-sm">Across all platforms</p>
            </div>
          </div>
          
          {/* Recent Content */}
          <div className="mb-8">
            <div className="flex justify-between items-center mb-4">
              <h2 className="text-xl font-semibold">Recent Content</h2>
              <Link to="/upload" className="text-blue-600 hover:text-blue-800">
                View All
              </Link>
            </div>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {recentContent.map((content) => (
                <div key={content.id} className="bg-white rounded-lg shadow overflow-hidden">
                  <div className="h-40 bg-gray-200">
                    {content.thumbnail_url ? (
                      <img 
                        src={content.thumbnail_url} 
                        alt={content.title} 
                        className="w-full h-full object-cover"
                      />
                    ) : (
                      <div className="w-full h-full flex items-center justify-center bg-gray-100">
                        <span className="text-gray-400">No preview</span>
                      </div>
                    )}
                  </div>
                  <div className="p-4">
                    <h3 className="font-semibold mb-1 truncate">{content.title}</h3>
                    <div className="flex justify-between items-center">
                      <span className="text-sm text-gray-500 capitalize">{content.type}</span>
                      <span className={`text-xs px-2 py-1 rounded-full ${
                        content.status === 'completed' ? 'bg-green-100 text-green-800' :
                        content.status === 'processing' ? 'bg-yellow-100 text-yellow-800' :
                        content.status === 'analyzed' ? 'bg-blue-100 text-blue-800' :
                        'bg-gray-100 text-gray-800'
                      }`}>
                        {content.status}
                      </span>
                    </div>
                    <div className="mt-4">
                      <Link 
                        to={`/create/${content.id}`} 
                        className="text-blue-600 hover:text-blue-800 text-sm font-medium"
                      >
                        Create Video →
                      </Link>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
          
          {/* Recent Videos */}
          <div>
            <div className="flex justify-between items-center mb-4">
              <h2 className="text-xl font-semibold">Recent Videos</h2>
              <Link to="/analytics" className="text-blue-600 hover:text-blue-800">
                View Analytics
              </Link>
            </div>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {recentVideos.map((video) => (
                <div key={video.id} className="bg-white rounded-lg shadow overflow-hidden">
                  <div className="h-40 bg-gray-200 relative">
                    {video.thumbnail_url ? (
                      <>
                        <img 
                          src={video.thumbnail_url} 
                          alt={video.title} 
                          className="w-full h-full object-cover"
                        />
                        <div className="absolute inset-0 flex items-center justify-center">
                          <div className="w-12 h-12 rounded-full bg-black bg-opacity-50 flex items-center justify-center">
                            <div className="w-0 h-0 border-t-8 border-t-transparent border-l-12 border-l-white border-b-8 border-b-transparent ml-1"></div>
                          </div>
                        </div>
                      </>
                    ) : (
                      <div className="w-full h-full flex items-center justify-center bg-gray-100">
                        <span className="text-gray-400">No preview</span>
                      </div>
                    )}
                  </div>
                  <div className="p-4">
                    <h3 className="font-semibold mb-1 truncate">{video.title}</h3>
                    <div className="flex justify-between items-center">
                      <span className="text-sm text-gray-500">TikTok</span>
                      <span className="text-xs px-2 py-1 rounded-full bg-green-100 text-green-800">
                        Published
                      </span>
                    </div>
                    <div className="mt-4 flex justify-between">
                      <span className="text-sm text-gray-500">
                        <span className="font-medium">1.2K</span> views
                      </span>
                      <Link 
                        to={`/analytics?video=${video.id}`} 
                        className="text-blue-600 hover:text-blue-800 text-sm font-medium"
                      >
                        View Stats →
                      </Link>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </>
      )}
    </div>
  );
};

export default Dashboard;
