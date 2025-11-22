# Deploying to Vercel

This guide explains how to deploy MazeRunner X to Vercel.

## Quick Start (Easiest Method)

1. **Build the game locally**:
   ```bash
   pip install pygbag
   pygbag --build main.py
   ```

2. **Install Vercel CLI** (if not already installed):
   ```bash
   npm install -g vercel
   ```

3. **Deploy from the build directory**:
   ```bash
   cd build/web
   vercel
   ```
   Follow the prompts, then run `vercel --prod` for production.

## Detailed Steps

### Method 1: Deploy Static Files (Recommended)

Since Vercel doesn't natively support Python builds, the easiest way is to build locally and deploy the static files:

1. **Build the project**:
   ```bash
   pip install pygbag
   pygbag --build main.py
   ```
   This creates a `build/web` directory with all static files.

2. **Deploy to Vercel**:
   ```bash
   # Option A: Deploy from build/web directory
   cd build/web
   vercel
   
   # Option B: Deploy from root with output directory
   vercel --cwd build/web
   ```

3. **For production**:
   ```bash
   vercel --prod
   ```

### Method 2: Include Build Files in Git (For CI/CD)

If you want automatic deployments from GitHub:

1. **Temporarily update .gitignore**:
   - Comment out `build/` or change to `build/!web/` to allow `build/web/`

2. **Build and commit**:
   ```bash
   pip install pygbag
   pygbag --build main.py
   git add build/web
   git commit -m "Add web build files"
   git push
   ```

3. **Connect to Vercel**:
   - Go to [vercel.com](https://vercel.com)
   - Click "New Project"
   - Import your GitHub repository
   - Set **Output Directory** to `build/web`
   - Deploy!

### Method 3: Use GitHub Actions (Advanced)

See `.github/workflows/deploy.yml` for automated build and deployment.

## Configuration

The `vercel.json` file is configured with:
- ✅ Proper WASM MIME types (`application/wasm`)
- ✅ CORS headers for WebAssembly
- ✅ Routing to serve `index.html` for all routes
- ✅ Cache headers for static assets

## Troubleshooting

### "Build directory not found"

Make sure you've built the project first:
```bash
pygbag --build main.py
```

### WASM files not loading

The `vercel.json` includes the correct headers. If issues persist:
1. Check browser console for CORS errors
2. Verify WASM files are in `build/web/`
3. Check that `Content-Type: application/wasm` header is set

### Game not starting

1. **Check browser console** for errors
2. **Verify async/await**: Make sure `main()` is `async def main()`
3. **Check file paths**: pygbag handles this automatically, but verify `index.html` exists

### Vercel build fails

Vercel doesn't support Python builds natively. Use one of these:
- **Option A**: Build locally, deploy static files (Method 1)
- **Option B**: Include `build/web` in git (Method 2)
- **Option C**: Use GitHub Actions to build (Method 3)

## File Structure After Build

```
build/web/
├── index.html          # Main entry point
├── main.data           # Game data
├── main.js             # JavaScript loader
├── main.wasm           # WebAssembly binary
└── ...                 # Other assets
```

## Notes

- ✅ The game uses async/await for pygbag compatibility (already done!)
- ✅ All static assets are served from `build/web`
- ✅ The game runs entirely client-side (no server needed)
- ⚠️ First load may take a moment as WASM files download (~1-5MB)
- ⚠️ Vercel free tier has limits on build minutes and bandwidth

## Next Steps

After deployment:
1. Your game will be available at `https://your-project.vercel.app`
2. You can add a custom domain in Vercel dashboard
3. Enable automatic deployments from your Git repository

