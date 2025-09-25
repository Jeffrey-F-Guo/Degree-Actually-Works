import { useEffect, useMemo } from 'react';
import { useParams, useSearchParams, Navigate } from 'react-router-dom';
import { GraphCanvas } from '@/components/graph/GraphCanvas';
import { ChecklistPanel } from '@/components/checklist/ChecklistPanel';
import { NodeDrawer } from '@/components/node/NodeDrawer';
import { TopNav } from '@/components/layout/TopNav';
import { useRoadmapStore } from '@/store/roadmapStore';
import { Button } from '@/components/ui/button';
import { Panel, PanelGroup, PanelResizeHandle } from 'react-resizable-panels';
import { Sidebar, Menu } from 'lucide-react';
import { cn } from '@/lib/utils';
import { RoadmapPath } from '@/types/roadmap';

// Import the paths data
import pathsData from '@/data/paths.json';

export const PathView = () => {
  const { slug } = useParams<{ slug: string }>();
  const [searchParams] = useSearchParams();
  const { setCurrentPath, loadFromShareableUrl } = useRoadmapStore();

  const currentPath = useMemo(() => {
    return pathsData.paths.find(path => path.slug === slug) as RoadmapPath | undefined;
  }, [slug]);

  useEffect(() => {
    if (currentPath) {
      setCurrentPath(currentPath);
      
      // Handle shared URLs
      const shareParam = searchParams.get('share');
      if (shareParam) {
        const success = loadFromShareableUrl(window.location.href);
        if (!success) {
          console.warn('Failed to load shared progress');
        }
      }
    }
  }, [currentPath, setCurrentPath, searchParams, loadFromShareableUrl]);

  if (!currentPath) {
    return <Navigate to="/" replace />;
  }

  return (
    <div className="h-screen flex flex-col bg-background">
      <TopNav currentPath={currentPath} allPaths={pathsData.paths as RoadmapPath[]} />
      
      <div className="flex-1 overflow-hidden">
        <PanelGroup direction="horizontal" className="h-full">
          {/* Main Graph Area */}
          <Panel defaultSize={70} minSize={50}>
            <div className="h-full relative">
              <GraphCanvas path={currentPath} />
            </div>
          </Panel>
          
          <PanelResizeHandle className="w-2 bg-border hover:bg-border/80 transition-colors" />
          
          {/* Checklist Sidebar */}
          <Panel defaultSize={30} minSize={25} maxSize={50}>
            <ChecklistPanel path={currentPath} className="h-full" />
          </Panel>
        </PanelGroup>
      </div>

      {/* Node Detail Drawer */}
      <NodeDrawer path={currentPath} />
    </div>
  );
};