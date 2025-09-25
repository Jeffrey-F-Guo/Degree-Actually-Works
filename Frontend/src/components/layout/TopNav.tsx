import { useState } from 'react';
import { Link, useParams } from 'react-router-dom';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from '@/components/ui/dialog';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { toast } from '@/components/ui/use-toast';
import {
  Menu,
  Search,
  Download,
  Upload,
  Share,
  Home,
  BookOpen,
  Copy,
  Check,
} from 'lucide-react';
import { useRoadmapStore } from '@/store/roadmapStore';
import { RoadmapPath } from '@/types/roadmap';
import { cn } from '@/lib/utils';

interface TopNavProps {
  currentPath?: RoadmapPath;
  allPaths: RoadmapPath[];
}

export const TopNav = ({ currentPath, allPaths }: TopNavProps) => {
  const { slug } = useParams();
  const {
    searchQuery,
    setSearchQuery,
    exportProgress,
    importProgress,
    generateShareableUrl,
  } = useRoadmapStore();
  
  const [isShareDialogOpen, setIsShareDialogOpen] = useState(false);
  const [isImportDialogOpen, setIsImportDialogOpen] = useState(false);
  const [importData, setImportData] = useState('');
  const [shareUrl, setShareUrl] = useState('');
  const [copied, setCopied] = useState(false);

  const handleExport = () => {
    if (!currentPath) return;
    
    const data = exportProgress(currentPath.slug);
    const blob = new Blob([data], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `wwu-cs-${currentPath.slug}-progress.json`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
    
    toast({
      title: "Progress Exported",
      description: "Your progress has been downloaded as a JSON file.",
    });
  };

  const handleImport = () => {
    if (!currentPath || !importData) return;
    
    const success = importProgress(currentPath.slug, importData);
    if (success) {
      toast({
        title: "Progress Imported",
        description: "Your progress has been successfully imported.",
      });
      setIsImportDialogOpen(false);
      setImportData('');
    } else {
      toast({
        title: "Import Failed",
        description: "The file format is invalid. Please check your JSON data.",
        variant: "destructive",
      });
    }
  };

  const handleShare = () => {
    if (!currentPath) return;
    
    const url = generateShareableUrl(currentPath.slug);
    setShareUrl(url);
    setIsShareDialogOpen(true);
  };

  const handleCopyUrl = async () => {
    try {
      await navigator.clipboard.writeText(shareUrl);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
      toast({
        title: "Link Copied",
        description: "Share link has been copied to clipboard.",
      });
    } catch (err) {
      toast({
        title: "Copy Failed",
        description: "Failed to copy link to clipboard.",
        variant: "destructive",
      });
    }
  };

  return (
    <nav className="sticky top-0 z-50 w-full border-b border-border bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60">
      <div className="container flex h-14 items-center">
        {/* Logo/Brand */}
        <div className="mr-4 hidden md:flex">
          <Link to="/" className="mr-6 flex items-center space-x-2">
            <div className="font-bold text-lg text-wwu-primary">
              WWU CS Roadmaps
            </div>
          </Link>
        </div>

        {/* Mobile menu */}
        <div className="mr-4 flex md:hidden">
          <DropdownMenu>
            <DropdownMenuTrigger asChild>
              <Button variant="ghost" size="sm">
                <Menu className="h-4 w-4" />
              </Button>
            </DropdownMenuTrigger>
            <DropdownMenuContent align="start" className="w-56">
              <DropdownMenuItem asChild>
                <Link to="/" className="flex items-center">
                  <Home className="mr-2 h-4 w-4" />
                  Home
                </Link>
              </DropdownMenuItem>
              <DropdownMenuItem asChild>
                <Link to="/resources" className="flex items-center">
                  <BookOpen className="mr-2 h-4 w-4" />
                  Resources
                </Link>
              </DropdownMenuItem>
              <DropdownMenuSeparator />
              {allPaths.map((path) => (
                <DropdownMenuItem key={path.slug} asChild>
                  <Link to={`/path/${path.slug}`}>
                    {path.name}
                  </Link>
                </DropdownMenuItem>
              ))}
            </DropdownMenuContent>
          </DropdownMenu>
        </div>

        {/* Desktop navigation */}
        <div className="hidden md:flex mr-6 space-x-6">
          <Link
            to="/"
            className="text-sm font-medium transition-colors hover:text-wwu-primary"
          >
            Home
          </Link>
          <Link
            to="/resources"
            className="text-sm font-medium transition-colors hover:text-wwu-primary"
          >
            Resources
          </Link>
        </div>

        {/* Path selector */}
        {slug && (
          <div className="hidden sm:flex mr-4">
            <DropdownMenu>
              <DropdownMenuTrigger asChild>
                <Button variant="outline" size="sm">
                  {currentPath?.name || 'Select Path'}
                </Button>
              </DropdownMenuTrigger>
              <DropdownMenuContent>
                {allPaths.map((path) => (
                  <DropdownMenuItem key={path.slug} asChild>
                    <Link 
                      to={`/path/${path.slug}`}
                      className={cn(
                        slug === path.slug && "bg-accent"
                      )}
                    >
                      {path.name}
                    </Link>
                  </DropdownMenuItem>
                ))}
              </DropdownMenuContent>
            </DropdownMenu>
          </div>
        )}

        {/* Search */}
        {currentPath && (
          <div className="flex-1 max-w-md mx-4">
            <div className="relative">
              <Search className="absolute left-2 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
              <Input
                placeholder="Search courses..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="pl-8"
              />
            </div>
          </div>
        )}

        {/* Actions */}
        {currentPath && (
          <div className="flex items-center space-x-2">
            <Button
              variant="outline"
              size="sm"
              onClick={handleShare}
            >
              <Share className="h-4 w-4" />
              <span className="hidden sm:ml-2 sm:inline">Share</span>
            </Button>
            
            <DropdownMenu>
              <DropdownMenuTrigger asChild>
                <Button variant="outline" size="sm">
                  <Download className="h-4 w-4" />
                  <span className="hidden sm:ml-2 sm:inline">Data</span>
                </Button>
              </DropdownMenuTrigger>
              <DropdownMenuContent align="end">
                <DropdownMenuItem onClick={handleExport}>
                  <Download className="mr-2 h-4 w-4" />
                  Export Progress
                </DropdownMenuItem>
                <DropdownMenuItem onClick={() => setIsImportDialogOpen(true)}>
                  <Upload className="mr-2 h-4 w-4" />
                  Import Progress
                </DropdownMenuItem>
              </DropdownMenuContent>
            </DropdownMenu>
          </div>
        )}
      </div>

      {/* Share Dialog */}
      <Dialog open={isShareDialogOpen} onOpenChange={setIsShareDialogOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Share Your Progress</DialogTitle>
            <DialogDescription>
              Anyone with this link can view your current progress on the {currentPath?.name} roadmap.
            </DialogDescription>
          </DialogHeader>
          <div className="space-y-4">
            <div className="flex space-x-2">
              <Input
                value={shareUrl}
                readOnly
                className="flex-1"
              />
              <Button onClick={handleCopyUrl} size="sm">
                {copied ? <Check className="h-4 w-4" /> : <Copy className="h-4 w-4" />}
              </Button>
            </div>
          </div>
          <DialogFooter>
            <Button onClick={() => setIsShareDialogOpen(false)}>Close</Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* Import Dialog */}
      <Dialog open={isImportDialogOpen} onOpenChange={setIsImportDialogOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Import Progress</DialogTitle>
            <DialogDescription>
              Paste the JSON data from a previously exported progress file.
            </DialogDescription>
          </DialogHeader>
          <div className="space-y-4">
            <div>
              <Label htmlFor="import-data">Progress Data (JSON)</Label>
              <Textarea
                id="import-data"
                placeholder="Paste your exported JSON data here..."
                value={importData}
                onChange={(e) => setImportData(e.target.value)}
                rows={10}
              />
            </div>
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => setIsImportDialogOpen(false)}>
              Cancel
            </Button>
            <Button onClick={handleImport} disabled={!importData.trim()}>
              Import
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </nav>
  );
};