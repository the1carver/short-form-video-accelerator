import React, { useState } from 'react';

interface InstantClipFormProps {
  duration: number;
  onCreateClip: (startTime: number, endTime: number, title: string) => void;
}

const InstantClipForm: React.FC<InstantClipFormProps> = ({ duration, onCreateClip }) => {
  const [startMinutes, setStartMinutes] = useState(0);
  const [startSeconds, setStartSeconds] = useState(0);
  const [endMinutes, setEndMinutes] = useState(0);
  const [endSeconds, setEndSeconds] = useState(10);
  const [title, setTitle] = useState('');
  
  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    
    const startTime = startMinutes * 60 + startSeconds;
    const endTime = endMinutes * 60 + endSeconds;
    
    if (endTime <= startTime) {
      alert('End time must be after start time');
      return;
    }
    
    if (endTime > duration) {
      alert('End time exceeds video duration');
      return;
    }
    
    onCreateClip(startTime, endTime, title);
  };
  
  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">Start Time</label>
          <div className="flex items-center">
            <input
              type="number"
              min="0"
              max={Math.floor(duration / 60)}
              value={startMinutes}
              onChange={(e) => setStartMinutes(parseInt(e.target.value))}
              className="w-20 px-3 py-2 border rounded-md"
            />
            <span className="mx-2">min</span>
            <input
              type="number"
              min="0"
              max="59"
              value={startSeconds}
              onChange={(e) => setStartSeconds(parseInt(e.target.value))}
              className="w-20 px-3 py-2 border rounded-md"
            />
            <span className="ml-2">sec</span>
          </div>
        </div>
        
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">End Time</label>
          <div className="flex items-center">
            <input
              type="number"
              min="0"
              max={Math.floor(duration / 60)}
              value={endMinutes}
              onChange={(e) => setEndMinutes(parseInt(e.target.value))}
              className="w-20 px-3 py-2 border rounded-md"
            />
            <span className="mx-2">min</span>
            <input
              type="number"
              min="0"
              max="59"
              value={endSeconds}
              onChange={(e) => setEndSeconds(parseInt(e.target.value))}
              className="w-20 px-3 py-2 border rounded-md"
            />
            <span className="ml-2">sec</span>
          </div>
        </div>
      </div>
      
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-1">Clip Title</label>
        <input
          type="text"
          value={title}
          onChange={(e) => setTitle(e.target.value)}
          placeholder="Enter a title for your clip"
          className="w-full px-3 py-2 border rounded-md"
          required
        />
      </div>
      
      <button
        type="submit"
        className="w-full px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
      >
        Create Instant Clip
      </button>
    </form>
  );
};

export default InstantClipForm;
