import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import api from '../lib/api';
import { showError, showSuccess } from '../components/ui/toast-utils';
import { ContentItem, Template, VideoSegment } from '../types';
import TimelineEditor from '../components/editor/TimelineEditor';
import InstantClipForm from '../components/editor/InstantClipForm';

const VideoCreationPage: React.FC = () => {
  const { contentId } = useParams<{ contentId: string }>();
  const navigate = useNavigate();
  
  const [content, setContent] = useState<ContentItem | null>(null);
  const [selectedTemplate, setSelectedTemplate] = useState<string>('');
  const [templates, setTemplates] = useState<Template[]>([]);
  const [loading, setLoading] = useState(true);
  const [processing, setProcessing] = useState(false);
  const [currentStep, setCurrentStep] = useState<'segments' | 'template' | 'preview'>('segments');
  const [editMode, setEditMode] = useState<'list' | 'timeline' | 'instant'>('list');
  
  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);
        
        // In a real app, these would be parallel requests
        if (contentId) {
          const contentResponse = await api.endpoints.content.getContent(contentId);
          const templatesResponse = await api.endpoints.content.getTemplates();
          
          // Mock data for development
          const mockContent: ContentItem = {
            id: contentId,
            title: 'How to Optimize Your LinkedIn Profile',
            description: 'Learn the best practices for creating a standout LinkedIn profile that attracts recruiters and opportunities.',
            duration: 1245, // in seconds
            url: 'https://example.com/videos/linkedin-tips.mp4',
            thumbnail_url: 'https://via.placeholder.com/640x360?text=LinkedIn+Tips',
            created_at: '2025-03-20T14:30:00Z',
            segments: [
              {
                id: '1',
                start_time: 0,
                end_time: 120,
                transcript: 'Welcome to this guide on optimizing your LinkedIn profile. Today we\'ll cover the key elements that make your profile stand out to recruiters and potential connections.',
                confidence: 0.95,
                selected: false
              },
              {
                id: '2',
                start_time: 121,
                end_time: 240,
                transcript: 'First, let\'s talk about your profile photo. A professional headshot increases profile views by 14 times. Make sure it\'s recent and represents how you look in a professional setting.',
                confidence: 0.92,
                selected: false
              },
              {
                id: '3',
                start_time: 241,
                end_time: 360,
                transcript: 'Next, your headline. Don\'t just list your job title. Use this space to highlight your expertise and value proposition in 120 characters or less.',
                confidence: 0.88,
                selected: false
              },
              {
                id: '4',
                start_time: 361,
                end_time: 480,
                transcript: 'Your about section should tell your professional story in a compelling way. Include your achievements, skills, and what you\'re passionate about.',
                confidence: 0.91,
                selected: false
              },
              {
                id: '5',
                start_time: 481,
                end_time: 600,
                transcript: 'Skills and endorsements matter. List at least 5 key skills relevant to your industry and ask colleagues to endorse them.',
                confidence: 0.94,
                selected: false
              }
            ]
          };
          
          const mockTemplates: Template[] = [
            {
              id: '1',
              name: 'TikTok Explainer',
              description: 'Short, engaging explainer template optimized for TikTok with captions and music.',
              thumbnail_url: 'https://via.placeholder.com/300x500?text=TikTok+Explainer',
              aspect_ratio: '9:16',
              suitable_content_types: ['educational', 'tutorial'],
              caption_style: {
                font_family: 'Inter',
                font_size: 24,
                font_color: '#FFFFFF',
                background_color: '#000000B3',
                position: 'bottom'
              }
            },
            {
              id: '2',
              name: 'Product Showcase',
              description: 'Highlight your product features with this dynamic template.',
              thumbnail_url: 'https://via.placeholder.com/300x500?text=Product+Showcase',
              aspect_ratio: '9:16',
              suitable_content_types: ['product', 'demo'],
              caption_style: {
                font_family: 'Montserrat',
                font_size: 28,
                font_color: '#FFFFFF',
                background_color: '#3B82F6B3',
                position: 'bottom'
              }
            },
            {
              id: '3',
              name: 'Tutorial Steps',
              description: 'Break down complex processes into simple steps.',
              thumbnail_url: 'https://via.placeholder.com/300x500?text=Tutorial+Steps',
              aspect_ratio: '9:16',
              suitable_content_types: ['tutorial', 'educational'],
              caption_style: {
                font_family: 'Roboto',
                font_size: 26,
                font_color: '#333333',
                background_color: '#FFFFFFCC',
                position: 'middle'
              }
            }
          ];
          
          setContent(contentResponse?.data || mockContent);
          setTemplates(templatesResponse?.data || mockTemplates);
        }
      } catch (error) {
        console.error('Error fetching data:', error);
        showError('Failed to load content data');
      } finally {
        setLoading(false);
      }
    };
    
    fetchData();
  }, [contentId]);
  
  const handleSegmentToggle = (segmentId: string) => {
    if (!content) return;
    
    setContent({
      ...content,
      segments: content.segments.map((segment: any) => 
        segment.id === segmentId 
          ? { ...segment, selected: !segment.selected }
          : segment
      )
    });
  };
  
  const handleTemplateSelect = (templateId: string) => {
    setSelectedTemplate(templateId);
  };
  
  const handleNextStep = () => {
    if (currentStep === 'segments') {
      if (!content?.segments.some((segment: any) => segment.selected)) {
        showError('Please select at least one segment');
        return;
      }
      setCurrentStep('template');
    } else if (currentStep === 'template') {
      if (!selectedTemplate) {
        showError('Please select a template');
        return;
      }
      setCurrentStep('preview');
    }
  };
  
  const handlePreviousStep = () => {
    if (currentStep === 'template') {
      setCurrentStep('segments');
    } else if (currentStep === 'preview') {
      setCurrentStep('template');
    }
  };
  
  const handleCreateVideo = async () => {
    if (!content || !selectedTemplate) return;
    
    try {
      setProcessing(true);
      
      const selectedSegments = content.segments
        .filter((segment: VideoSegment) => segment.selected)
        .map((segment: VideoSegment) => segment.id);
      
      // In a real app, this would be an API call
      await api.endpoints.content.createVideo({
        contentId: content.id,
        templateId: selectedTemplate,
        segments: selectedSegments
      });
      
      // Mock successful response
      setTimeout(() => {
        setProcessing(false);
        showSuccess('Video created successfully!');
        navigate('/');
      }, 2000);
    } catch (error) {
      console.error('Error creating video:', error);
      showError('Failed to create video');
      setProcessing(false);
    }
  };
  
  const handleInstantClip = async (startTime: number, endTime: number, title: string) => {
    if (!content) return;
    
    try {
      setProcessing(true);
      
      const instantSegment = {
        id: `instant-${Date.now()}`,
        start_time: startTime,
        end_time: endTime,
        transcript: title,
        confidence: 1.0,
        selected: true
      };
      
      const updatedContent = {
        ...content,
        segments: [instantSegment]
      };
      setContent(updatedContent);
      
      setCurrentStep('template');
    } catch (error) {
      console.error('Error creating instant clip:', error);
      showError('Failed to create instant clip');
    } finally {
      setProcessing(false);
    }
  };

  const formatTime = (seconds: number) => {
    const minutes = Math.floor(seconds / 60);
    const remainingSeconds = Math.floor(seconds % 60);
    return `${minutes}:${remainingSeconds.toString().padStart(2, '0')}`;
  };
  
  if (loading) {
    return (
      <div className="flex justify-center items-center h-screen">
        <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-blue-500"></div>
      </div>
    );
  }
  
  if (!content) {
    return (
      <div className="container mx-auto px-4 py-8">
        <div className="bg-red-50 p-4 rounded-md">
          <p className="text-red-700">Content not found or failed to load.</p>
          <button
            onClick={() => navigate('/')}
            className="mt-4 px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 transition-colors"
          >
            Return to Dashboard
          </button>
        </div>
      </div>
    );
  }
  
  return (
    <div className="container mx-auto px-4 py-8">
      <div className="mb-8">
        <h1 className="text-3xl font-bold mb-2">{content.title}</h1>
        <p className="text-gray-600">{content.description}</p>
      </div>
      
      {/* Step indicator */}
      <div className="mb-8">
        <div className="flex items-center">
          <div className={`flex items-center justify-center w-10 h-10 rounded-full ${
            currentStep === 'segments' ? 'bg-blue-600 text-white' : 'bg-gray-200 text-gray-700'
          }`}>
            1
          </div>
          <div className={`flex-1 h-1 mx-2 ${
            currentStep === 'segments' ? 'bg-gray-200' : 'bg-blue-600'
          }`}></div>
          <div className={`flex items-center justify-center w-10 h-10 rounded-full ${
            currentStep === 'template' ? 'bg-blue-600 text-white' : currentStep === 'preview' ? 'bg-blue-600 text-white' : 'bg-gray-200 text-gray-700'
          }`}>
            2
          </div>
          <div className={`flex-1 h-1 mx-2 ${
            currentStep === 'preview' ? 'bg-blue-600' : 'bg-gray-200'
          }`}></div>
          <div className={`flex items-center justify-center w-10 h-10 rounded-full ${
            currentStep === 'preview' ? 'bg-blue-600 text-white' : 'bg-gray-200 text-gray-700'
          }`}>
            3
          </div>
        </div>
        <div className="flex justify-between mt-2">
          <span className={`text-sm ${currentStep === 'segments' ? 'text-blue-600 font-medium' : 'text-gray-500'}`}>
            Select Segments
          </span>
          <span className={`text-sm ${currentStep === 'template' ? 'text-blue-600 font-medium' : 'text-gray-500'}`}>
            Choose Template
          </span>
          <span className={`text-sm ${currentStep === 'preview' ? 'text-blue-600 font-medium' : 'text-gray-500'}`}>
            Preview and Create
          </span>
        </div>
      </div>
      
      {/* Content based on current step */}
      {currentStep === 'segments' && (
        <div className="bg-white rounded-lg shadow overflow-hidden">
          <div className="p-6 border-b">
            <h2 className="text-xl font-semibold">Select Content Segments</h2>
            <p className="text-gray-600 text-sm mt-1">
              Choose the segments you want to include in your short-form video.
            </p>
            
            {/* Mode selector */}
            <div className="flex mt-4 border rounded-lg overflow-hidden">
              <button
                className={`px-4 py-2 flex-1 ${
                  editMode === 'list' ? 'bg-blue-50 text-blue-600' : 'bg-white text-gray-600'
                }`}
                onClick={() => setEditMode('list')}
              >
                List View
              </button>
              <button
                className={`px-4 py-2 flex-1 ${
                  editMode === 'timeline' ? 'bg-blue-50 text-blue-600' : 'bg-white text-gray-600'
                }`}
                onClick={() => setEditMode('timeline')}
              >
                Timeline Editor
              </button>
              <button
                className={`px-4 py-2 flex-1 ${
                  editMode === 'instant' ? 'bg-blue-50 text-blue-600' : 'bg-white text-gray-600'
                }`}
                onClick={() => setEditMode('instant')}
              >
                Instant Clip
              </button>
            </div>
          </div>
          
          {editMode === 'timeline' && (
            <div className="p-6">
              <TimelineEditor
                videoUrl={content.url}
                duration={content.duration}
                segments={content.segments}
                onSegmentUpdate={(updatedSegments) => setContent({...content, segments: updatedSegments})}
              />
            </div>
          )}
          
          {editMode === 'instant' && (
            <div className="p-6">
              <InstantClipForm
                duration={content.duration}
                onCreateClip={(startTime, endTime, title) => handleInstantClip(startTime, endTime, title)}
              />
            </div>
          )}
          
          {editMode === 'list' && (
            <div className="divide-y">
            {content.segments.map((segment: VideoSegment) => (
              <div 
                key={segment.id} 
                className={`p-6 hover:bg-gray-50 cursor-pointer ${segment.selected ? 'bg-blue-50' : ''}`}
                onClick={() => handleSegmentToggle(segment.id)}
              >
                <div className="flex items-start">
                  <input
                    type="checkbox"
                    checked={segment.selected}
                    onChange={() => handleSegmentToggle(segment.id)}
                    className="mt-1 h-5 w-5 text-blue-600 rounded"
                  />
                  <div className="ml-4 flex-grow">
                    <div className="flex justify-between mb-2">
                      <span className="text-sm font-medium text-gray-500">
                        {formatTime(segment.start_time)} - {formatTime(segment.end_time)}
                      </span>
                      <span className="text-xs bg-green-100 text-green-800 px-2 py-1 rounded-full">
                        {Math.round(segment.confidence * 100)}% confidence
                      </span>
                    </div>
                    <p className="text-gray-700">{segment.transcript}</p>
                  </div>
                </div>
              </div>
            ))}
            </div>
          )}
        </div>
      )}
      
      {currentStep === 'template' && (
        <div className="bg-white rounded-lg shadow overflow-hidden">
          <div className="p-6 border-b">
            <h2 className="text-xl font-semibold">Choose a Template</h2>
            <p className="text-gray-600 text-sm mt-1">
              Select a template for your short-form video.
            </p>
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6 p-6">
            {templates.map((template) => (
              <div 
                key={template.id} 
                className={`border rounded-lg overflow-hidden cursor-pointer transition-all ${
                  selectedTemplate === template.id 
                    ? 'border-blue-500 ring-2 ring-blue-500 ring-opacity-50' 
                    : 'border-gray-200 hover:border-blue-300'
                }`}
                onClick={() => handleTemplateSelect(template.id)}
              >
                <div className="h-64 bg-gray-100">
                  <img 
                    src={template.thumbnail_url} 
                    alt={template.name} 
                    className="w-full h-full object-cover"
                  />
                </div>
                <div className="p-4">
                  <h3 className="font-medium">{template.name}</h3>
                  <p className="text-sm text-gray-600 mt-1">{template.description}</p>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
      
      {currentStep === 'preview' && (
        <div className="bg-white rounded-lg shadow overflow-hidden">
          <div className="p-6 border-b">
            <h2 className="text-xl font-semibold">Preview and Create</h2>
            <p className="text-gray-600 text-sm mt-1">
              Review your selections and create your short-form video.
            </p>
          </div>
          
          <div className="p-6">
            <div className="mb-6">
              <h3 className="font-medium mb-2">Selected Template</h3>
              <div className="flex items-center">
                {selectedTemplate && (
                  <>
                    <div className="w-16 h-16 bg-gray-100 rounded overflow-hidden">
                      <img 
                        src={templates.find(t => t.id === selectedTemplate)?.thumbnail_url} 
                        alt="Template" 
                        className="w-full h-full object-cover"
                      />
                    </div>
                    <div className="ml-4">
                      <p className="font-medium">{templates.find(t => t.id === selectedTemplate)?.name}</p>
                      <p className="text-sm text-gray-600">{templates.find(t => t.id === selectedTemplate)?.description}</p>
                    </div>
                  </>
                )}
              </div>
            </div>
            
            <div>
              <h3 className="font-medium mb-2">Selected Segments</h3>
              <div className="border rounded-lg divide-y">
                {content.segments
                  .filter((segment: VideoSegment) => segment.selected)
                  .map((segment: VideoSegment) => (
                    <div key={segment.id} className="p-4">
                      <div className="flex justify-between mb-1">
                        <span className="text-sm font-medium text-gray-500">
                          {formatTime(segment.start_time)} - {formatTime(segment.end_time)}
                        </span>
                      </div>
                      <p className="text-sm text-gray-700">{segment.transcript}</p>
                    </div>
                  ))}
              </div>
              
              {content.segments.filter((segment: VideoSegment) => segment.selected).length === 0 && (
                <p className="text-red-600 text-sm">No segments selected. Please go back and select segments.</p>
              )}
            </div>
          </div>
        </div>
      )}
      
      {/* Navigation buttons */}
      <div className="mt-8 flex justify-between">
        <button
          onClick={handlePreviousStep}
          className={`px-4 py-2 border border-gray-300 rounded text-gray-700 hover:bg-gray-50 ${
            currentStep === 'segments' ? 'invisible' : ''
          }`}
        >
          Previous
        </button>
        
        {currentStep === 'preview' ? (
          <button
            onClick={handleCreateVideo}
            disabled={processing || content.segments.filter((segment: VideoSegment) => segment.selected).length === 0}
            className={`px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 transition-colors ${
              (processing || content.segments.filter((segment: VideoSegment) => segment.selected).length === 0) ? 'opacity-50 cursor-not-allowed' : ''
            }`}
          >
            {processing ? (
              <span className="flex items-center">
                <svg className="animate-spin -ml-1 mr-2 h-4 w-4 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                  <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                </svg>
                Creating Video...
              </span>
            ) : (
              'Create Video'
            )}
          </button>
        ) : (
          <button
            onClick={handleNextStep}
            className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 transition-colors"
          >
            Next
          </button>
        )}
      </div>
    </div>
  );
};

export default VideoCreationPage;
