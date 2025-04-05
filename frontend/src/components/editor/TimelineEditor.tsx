import React, { useState, useRef, useEffect } from 'react';
import { VideoSegment } from '../../types';

interface TimelineEditorProps {
  videoUrl: string;
  duration: number;
  segments: VideoSegment[];
  onSegmentUpdate: (segments: VideoSegment[]) => void;
}

const TimelineEditor: React.FC<TimelineEditorProps> = ({ 
  videoUrl, 
  duration, 
  segments, 
  onSegmentUpdate 
}) => {
  const [selectedSegment, setSelectedSegment] = useState<string | null>(null);
  const [isDragging, setIsDragging] = useState<'start' | 'end' | 'position' | null>(null);
  const timelineRef = useRef<HTMLDivElement>(null);
  const videoRef = useRef<HTMLVideoElement>(null);
  
  const formatTime = (seconds: number) => {
    const minutes = Math.floor(seconds / 60);
    const remainingSeconds = Math.floor(seconds % 60);
    return `${minutes}:${remainingSeconds.toString().padStart(2, '0')}`;
  };
  
  const timeToPosition = (time: number) => {
    return (time / duration) * 100;
  };
  
  const positionToTime = (position: number) => {
    const percent = position / (timelineRef.current?.clientWidth || 1);
    return percent * duration;
  };
  
  const handleTimelineClick = (e: React.MouseEvent) => {
    if (!timelineRef.current) return;
    
    const rect = timelineRef.current.getBoundingClientRect();
    const clickPosition = e.clientX - rect.left;
    const time = positionToTime(clickPosition);
    
    if (videoRef.current) {
      videoRef.current.currentTime = time;
    }
  };
  
  const handleDragStart = (segmentId: string, type: 'start' | 'end' | 'position') => (e: React.MouseEvent) => {
    e.stopPropagation();
    setSelectedSegment(segmentId);
    setIsDragging(type);
  };
  
  const handleDrag = (e: React.MouseEvent) => {
    if (!isDragging || !selectedSegment || !timelineRef.current) return;
    
    const rect = timelineRef.current.getBoundingClientRect();
    const position = Math.max(0, Math.min(e.clientX - rect.left, rect.width));
    const time = positionToTime(position);
    
    const updatedSegments = segments.map(segment => {
      if (segment.id === selectedSegment) {
        if (isDragging === 'start') {
          return { 
            ...segment, 
            start_time: Math.min(time, segment.end_time - 1) 
          };
        } else if (isDragging === 'end') {
          return { 
            ...segment, 
            end_time: Math.max(time, segment.start_time + 1) 
          };
        } else if (isDragging === 'position') {
          const segmentDuration = segment.end_time - segment.start_time;
          const newStart = Math.max(0, Math.min(time, duration - segmentDuration));
          return {
            ...segment,
            start_time: newStart,
            end_time: newStart + segmentDuration
          };
        }
      }
      return segment;
    });
    
    onSegmentUpdate(updatedSegments);
    
    if (videoRef.current) {
      videoRef.current.currentTime = time;
    }
  };
  
  const handleDragEnd = () => {
    setIsDragging(null);
  };
  
  useEffect(() => {
    const handleMouseMove = (e: MouseEvent) => {
      if (isDragging) {
        handleDrag(e as unknown as React.MouseEvent);
      }
    };
    
    const handleMouseUp = () => {
      handleDragEnd();
    };
    
    document.addEventListener('mousemove', handleMouseMove);
    document.addEventListener('mouseup', handleMouseUp);
    
    return () => {
      document.removeEventListener('mousemove', handleMouseMove);
      document.removeEventListener('mouseup', handleMouseUp);
    };
  }, [isDragging, selectedSegment]);
  
  return (
    <div className="mb-8">
      <div className="mb-4">
        <video 
          ref={videoRef}
          src={videoUrl} 
          controls
          className="w-full rounded-lg" 
        />
      </div>
      
      <div className="mb-2 flex justify-between text-sm text-gray-500">
        <span>{formatTime(0)}</span>
        <span>{formatTime(duration / 2)}</span>
        <span>{formatTime(duration)}</span>
      </div>
      
      <div 
        ref={timelineRef}
        className="relative h-12 bg-gray-200 rounded-lg cursor-pointer"
        onClick={handleTimelineClick}
      >
        {/* Time markers */}
        <div className="absolute inset-x-0 top-0 flex justify-between px-2">
          {Array.from({ length: 10 }).map((_, i) => (
            <div key={i} className="h-2 w-px bg-gray-400" />
          ))}
        </div>
        
        {/* Segments */}
        {segments.map(segment => (
          <div
            key={segment.id}
            className={`absolute h-8 bottom-0 rounded-md ${
              segment.selected ? 'bg-blue-500' : 'bg-blue-300'
            } ${selectedSegment === segment.id ? 'ring-2 ring-blue-700' : ''}`}
            style={{
              left: `${timeToPosition(segment.start_time)}%`,
              width: `${timeToPosition(segment.end_time - segment.start_time)}%`
            }}
            onClick={(e) => {
              e.stopPropagation();
              setSelectedSegment(segment.id);
            }}
          >
            {/* Drag handles */}
            <div 
              className="absolute left-0 top-0 w-2 h-full cursor-ew-resize"
              onMouseDown={handleDragStart(segment.id, 'start')}
            />
            <div 
              className="absolute right-0 top-0 w-2 h-full cursor-ew-resize"
              onMouseDown={handleDragStart(segment.id, 'end')}
            />
            <div 
              className="absolute inset-x-2 top-0 h-full cursor-move"
              onMouseDown={handleDragStart(segment.id, 'position')}
            >
              <span className="text-xs text-white px-1 truncate block">
                {formatTime(segment.start_time)} - {formatTime(segment.end_time)}
              </span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default TimelineEditor;
