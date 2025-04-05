export interface VideoSegment {
  id: string;
  start_time: number;
  end_time: number;
  transcript: string;
  confidence: number;
  selected: boolean;
}

export interface ContentItem {
  id: string;
  title: string;
  description: string;
  duration: number;
  url: string;
  thumbnail_url: string;
  segments: VideoSegment[];
  created_at: string;
}

export interface CaptionStyle {
  font_family: string;
  font_size: number;
  font_color: string;
  background_color: string;
  position: string;
}

export interface Template {
  id: string;
  name: string;
  description: string;
  aspect_ratio: string;
  suitable_content_types: string[];
  thumbnail_url: string;
  caption_style: CaptionStyle;
  overlay_color?: string;
  intro_animation?: string;
  outro_animation?: string;
}
