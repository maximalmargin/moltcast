#!/bin/bash
# Deploy MoltCast podcast feed to Vercel
# Run from repo root: bash feed/deploy.sh

set -e

DEPLOY_DIR=$(mktemp -d)
echo "Building deploy package in $DEPLOY_DIR..."

# Copy feed files
cp feed/index.html "$DEPLOY_DIR/"
cp feed/rss.xml "$DEPLOY_DIR/"
cp feed/vercel.json "$DEPLOY_DIR/"

# Copy cover
cp cover.png "$DEPLOY_DIR/cover.jpg" 2>/dev/null || true
python3 -c "
from PIL import Image
img = Image.open('cover.png')
img = img.resize((600, 600), Image.LANCZOS)
img.save('$DEPLOY_DIR/cover.jpg', quality=80)
" 2>/dev/null || cp cover.png "$DEPLOY_DIR/cover.jpg"

# Copy episodes
mkdir -p "$DEPLOY_DIR/episodes/ep001"
cp episodes/ep001/episode-001-en.mp3 "$DEPLOY_DIR/episodes/ep001/"

echo "Deploying to Vercel..."
cd "$DEPLOY_DIR"
vercel --prod --yes

echo "Done! RSS feed at: https://your-domain/rss.xml"
rm -rf "$DEPLOY_DIR"
