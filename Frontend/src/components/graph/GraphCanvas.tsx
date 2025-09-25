import { useCallback, useEffect, useMemo } from 'react';
import ReactFlow, {
  Node,
  Edge,
  addEdge,
  useNodesState,
  useEdgesState,
  Controls,
  MiniMap,
  Background,
  Connection,
  ReactFlowProvider,
  Panel,
  useReactFlow,
} from 'reactflow';
import 'reactflow/dist/style.css';

import { CourseNode } from './CourseNode';
import { RoadmapPath } from '@/types/roadmap';
import { useRoadmapStore } from '@/store/roadmapStore';
import { Button } from '@/components/ui/button';
import { ZoomIn, ZoomOut, Maximize } from 'lucide-react';

const nodeTypes = {
  courseNode: CourseNode,
};

interface GraphCanvasProps {
  path: RoadmapPath;
}

// Layout algorithm to position nodes
const calculateLayout = (path: RoadmapPath) => {
  const nodes: Node[] = [];
  const edges: Edge[] = [];
  
  let yOffset = 0;
  const groupSpacing = 200;
  const nodeSpacing = { x: 280, y: 120 };
  
  // Create a map to store node positions and track dependencies
  const nodePositions = new Map<string, { x: number; y: number; level: number }>();
  
  path.groups.forEach((group, groupIndex) => {
    // Calculate levels for topological sort
    const levels = new Map<string, number>();
    const visited = new Set<string>();
    
    const calculateLevel = (nodeId: string, nodes: typeof group.nodes): number => {
      if (visited.has(nodeId)) return levels.get(nodeId) || 0;
      visited.add(nodeId);
      
      const node = nodes.find(n => n.id === nodeId);
      if (!node || node.prereqs.length === 0) {
        levels.set(nodeId, 0);
        return 0;
      }
      
      const maxPrereqLevel = Math.max(
        ...node.prereqs.map(prereqId => {
          // Look for prereq in current group first, then other groups
          const prereqInGroup = nodes.find(n => n.id === prereqId);
          if (prereqInGroup) {
            return calculateLevel(prereqId, nodes);
          }
          // If not in current group, assume it's from a previous group
          return -1;
        })
      );
      
      const level = maxPrereqLevel + 1;
      levels.set(nodeId, level);
      return level;
    };
    
    // Calculate levels for all nodes in group
    group.nodes.forEach(node => {
      calculateLevel(node.id, group.nodes);
    });
    
    // Group nodes by level
    const nodesByLevel = new Map<number, typeof group.nodes>();
    group.nodes.forEach(node => {
      const level = levels.get(node.id) || 0;
      if (!nodesByLevel.has(level)) {
        nodesByLevel.set(level, []);
      }
      nodesByLevel.get(level)!.push(node);
    });
    
    // Position nodes
    const maxLevel = Math.max(...Array.from(levels.values()));
    
    for (let level = 0; level <= maxLevel; level++) {
      const nodesAtLevel = nodesByLevel.get(level) || [];
      const levelWidth = nodesAtLevel.length * nodeSpacing.x;
      const startX = -levelWidth / 2;
      
      nodesAtLevel.forEach((node, index) => {
        const x = startX + (index + 0.5) * nodeSpacing.x;
        const y = yOffset + (level * nodeSpacing.y);
        
        nodePositions.set(node.id, { x, y, level });
      });
    }
    
    yOffset += (maxLevel + 1) * nodeSpacing.y + groupSpacing;
  });
  
  // Create nodes
  path.groups.forEach(group => {
    group.nodes.forEach(node => {
      const position = nodePositions.get(node.id) || { x: 0, y: 0, level: 0 };
      
      nodes.push({
        id: node.id,
        type: 'courseNode',
        position,
        data: node,
      });
    });
  });
  
  // Create edges
  path.groups.forEach(group => {
    group.nodes.forEach(node => {
      node.prereqs.forEach(prereqId => {
        // Only create edge if prereq exists in the path
        const prereqExists = path.groups.some(g => 
          g.nodes.some(n => n.id === prereqId)
        );
        
        if (prereqExists) {
          edges.push({
            id: `${prereqId}-${node.id}`,
            source: prereqId,
            target: node.id,
            type: 'smoothstep',
            animated: false,
          });
        }
      });
    });
  });
  
  return { nodes, edges };
};

const GraphCanvasInner = ({ path }: GraphCanvasProps) => {
  const { 
    getNodeStatus, 
    setSelectedNode, 
    setNodeDrawerOpen,
    searchQuery,
    hiddenGroups 
  } = useRoadmapStore();
  
  const { fitView, zoomIn, zoomOut } = useReactFlow();
  
  const { nodes: initialNodes, edges: initialEdges } = useMemo(() => 
    calculateLayout(path), [path]
  );
  
  // Add status and click handler to nodes
  const enrichedNodes = useMemo(() => 
    initialNodes.map(node => ({
      ...node,
      data: {
        ...node.data,
        status: getNodeStatus(path.slug, node.id),
        onClick: (nodeId: string) => {
          setSelectedNode(nodeId);
          setNodeDrawerOpen(true);
        },
      },
      hidden: hiddenGroups.some(hiddenGroup => 
        path.groups.find(group => 
          group.title === hiddenGroup && 
          group.nodes.some(n => n.id === node.id)
        )
      ) || (searchQuery && !node.data.title.toLowerCase().includes(searchQuery.toLowerCase()) &&
        !node.data.tags.some(tag => tag.toLowerCase().includes(searchQuery.toLowerCase()))),
    })), 
    [initialNodes, getNodeStatus, path.slug, setSelectedNode, setNodeDrawerOpen, hiddenGroups, searchQuery]
  );
  
  const [nodes, setNodes, onNodesChange] = useNodesState(enrichedNodes);
  const [edges, setEdges, onEdgesChange] = useEdgesState(initialEdges);
  
  // Update nodes when status changes
  useEffect(() => {
    setNodes(enrichedNodes);
  }, [enrichedNodes, setNodes]);
  
  const onConnect = useCallback(
    (params: Connection) => setEdges((eds) => addEdge(params, eds)),
    [setEdges]
  );
  
  return (
    <div className="w-full h-full bg-surface">
      <ReactFlow
        nodes={nodes}
        edges={edges}
        onNodesChange={onNodesChange}
        onEdgesChange={onEdgesChange}
        onConnect={onConnect}
        nodeTypes={nodeTypes}
        fitView
        fitViewOptions={{ padding: 0.1 }}
        minZoom={0.1}
        maxZoom={2}
        defaultViewport={{ x: 0, y: 0, zoom: 0.8 }}
      >
        <Controls showInteractive={false} className="bg-card border border-border" />
        <MiniMap 
          className="bg-card border border-border"
          maskColor="rgb(0, 0, 0, 0.1)"
          nodeColor={(node) => {
            const status = (node.data as any)?.status;
            switch (status) {
              case 'completed': return 'hsl(var(--success))';
              case 'in-progress': return 'hsl(var(--warning))';
              case 'skipped': return 'hsl(var(--muted-foreground))';
              default: return 'hsl(var(--wwu-primary))';
            }
          }}
        />
        <Background color="hsl(var(--muted))" gap={20} />
        
        <Panel position="top-right" className="flex gap-2">
          <Button
            variant="outline"
            size="sm"
            onClick={() => zoomIn()}
            className="bg-card"
          >
            <ZoomIn className="w-4 h-4" />
          </Button>
          <Button
            variant="outline"
            size="sm"
            onClick={() => zoomOut()}
            className="bg-card"
          >
            <ZoomOut className="w-4 h-4" />
          </Button>
          <Button
            variant="outline"
            size="sm"
            onClick={() => fitView({ padding: 0.1 })}
            className="bg-card"
          >
            <Maximize className="w-4 h-4" />
          </Button>
        </Panel>
      </ReactFlow>
    </div>
  );
};

export const GraphCanvas = ({ path }: GraphCanvasProps) => {
  return (
    <ReactFlowProvider>
      <GraphCanvasInner path={path} />
    </ReactFlowProvider>
  );
};