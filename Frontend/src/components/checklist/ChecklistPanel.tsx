import { useMemo } from 'react';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Progress } from '@/components/ui/progress';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Separator } from '@/components/ui/separator';
import { 
  CheckCircle, 
  Clock, 
  Circle, 
  XCircle, 
  Search,
  Eye,
  EyeOff,
} from 'lucide-react';
import { useRoadmapStore } from '@/store/roadmapStore';
import { RoadmapPath, NodeStatus } from '@/types/roadmap';
import { cn } from '@/lib/utils';

interface ChecklistPanelProps {
  path: RoadmapPath;
  className?: string;
}

const statusIcons = {
  'not-started': Circle,
  'in-progress': Clock,
  'completed': CheckCircle,
  'skipped': XCircle,
};

const statusLabels = {
  'not-started': 'Not Started',
  'in-progress': 'In Progress',
  'completed': 'Completed',
  'skipped': 'Skipped',
};

const statusColors = {
  'not-started': 'text-muted-foreground',
  'in-progress': 'text-warning',
  'completed': 'text-success',
  'skipped': 'text-muted-foreground',
};

const nextStatus: Record<NodeStatus, NodeStatus> = {
  'not-started': 'in-progress',
  'in-progress': 'completed',
  'completed': 'skipped',
  'skipped': 'not-started',
};

export const ChecklistPanel = ({ path, className }: ChecklistPanelProps) => {
  const {
    getNodeStatus,
    setNodeStatus,
    getPathProgress,
    getGroupProgress,
    searchQuery,
    setSearchQuery,
    hiddenGroups,
    toggleGroupVisibility,
    setSelectedNode,
    setNodeDrawerOpen,
  } = useRoadmapStore();

  const pathProgress = getPathProgress(path.slug);

  const filteredGroups = useMemo(() => {
    if (!searchQuery) return path.groups;
    
    return path.groups.map(group => ({
      ...group,
      nodes: group.nodes.filter(node =>
        node.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
        node.code.toLowerCase().includes(searchQuery.toLowerCase()) ||
        node.tags.some(tag => tag.toLowerCase().includes(searchQuery.toLowerCase()))
      ),
    })).filter(group => group.nodes.length > 0);
  }, [path.groups, searchQuery]);

  const handleNodeClick = (nodeId: string) => {
    setSelectedNode(nodeId);
    setNodeDrawerOpen(true);
  };

  const handleStatusChange = (nodeId: string, currentStatus: NodeStatus) => {
    const newStatus = nextStatus[currentStatus];
    setNodeStatus(path.slug, nodeId, newStatus);
  };

  return (
    <div className={cn("flex flex-col h-full bg-card", className)}>
      {/* Header */}
      <div className="p-4 border-b border-border">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-lg font-semibold">Progress Checklist</h2>
          <Badge variant="outline" className="text-sm">
            {pathProgress.completed} / {pathProgress.total}
          </Badge>
        </div>
        
        <div className="space-y-3">
          <Progress value={pathProgress.percentage} className="h-2" />
          <div className="text-sm text-muted-foreground text-center">
            {pathProgress.percentage}% Complete
          </div>
        </div>
        
        {/* Search */}
        <div className="relative mt-4">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-muted-foreground" />
          <Input
            placeholder="Search courses, tags..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="pl-10"
          />
        </div>
      </div>

      {/* Groups */}
      <ScrollArea className="flex-1 custom-scrollbar">
        <div className="p-4 space-y-6">
          {filteredGroups.map((group) => {
            const isHidden = hiddenGroups.includes(group.title);
            const groupProgress = getGroupProgress(
              path.slug,
              group.nodes.map(n => n.id)
            );

            return (
              <div key={group.title} className="space-y-3">
                {/* Group Header */}
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={() => toggleGroupVisibility(group.title)}
                      className="p-1 h-auto"
                    >
                      {isHidden ? (
                        <EyeOff className="w-4 h-4" />
                      ) : (
                        <Eye className="w-4 h-4" />
                      )}
                    </Button>
                    <h3 className="font-medium text-foreground">{group.title}</h3>
                  </div>
                  <div className="flex items-center gap-2">
                    <Badge variant="secondary" className="text-xs">
                      {groupProgress.completed}/{groupProgress.total}
                    </Badge>
                    <div className="text-xs text-muted-foreground">
                      {groupProgress.percentage}%
                    </div>
                  </div>
                </div>

                <Progress value={groupProgress.percentage} className="h-1.5" />

                {/* Group Nodes */}
                {!isHidden && (
                  <div className="space-y-2 ml-4">
                    {group.nodes.map((node) => {
                      const status = getNodeStatus(path.slug, node.id);
                      const StatusIcon = statusIcons[status];

                      return (
                        <div
                          key={node.id}
                          className="flex items-center gap-3 p-3 rounded-lg border border-border hover:bg-muted/50 transition-colors group cursor-pointer"
                          onClick={() => handleNodeClick(node.id)}
                        >
                          <Button
                            variant="ghost"
                            size="sm"
                            onClick={(e) => {
                              e.stopPropagation();
                              handleStatusChange(node.id, status);
                            }}
                            className="p-1 h-auto hover:bg-transparent"
                          >
                            <StatusIcon 
                              className={cn("w-5 h-5", statusColors[status])} 
                            />
                          </Button>

                          <div className="flex-1 min-w-0">
                            <div className="flex items-center gap-2 mb-1">
                              <div className="text-xs text-muted-foreground font-mono">
                                {node.code}
                              </div>
                              <Badge 
                                variant={node.type === 'core' ? 'default' : 'secondary'}
                                className="text-xs"
                              >
                                {node.type === 'core' ? 'Core' : 'Elective'}
                              </Badge>
                            </div>
                            <div className="text-sm font-medium text-foreground group-hover:text-wwu-primary transition-colors">
                              {node.title}
                            </div>
                            {node.tags.length > 0 && (
                              <div className="flex flex-wrap gap-1 mt-1">
                                {node.tags.slice(0, 3).map((tag) => (
                                  <Badge
                                    key={tag}
                                    variant="outline"
                                    className="text-xs"
                                  >
                                    {tag}
                                  </Badge>
                                ))}
                                {node.tags.length > 3 && (
                                  <Badge variant="outline" className="text-xs">
                                    +{node.tags.length - 3}
                                  </Badge>
                                )}
                              </div>
                            )}
                          </div>

                          <div className="text-xs text-muted-foreground">
                            {statusLabels[status]}
                          </div>
                        </div>
                      );
                    })}
                  </div>
                )}

                {group !== filteredGroups[filteredGroups.length - 1] && (
                  <Separator className="mt-4" />
                )}
              </div>
            );
          })}
        </div>
      </ScrollArea>
    </div>
  );
};