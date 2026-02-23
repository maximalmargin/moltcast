#!/bin/bash
# Deploy MoltCast English feed to Vercel
# Run from repo root: bash feed-en/deploy.sh
set -e

DEPLOY_DIR=$(mktemp -d)
echo "Building English feed in $DEPLOY_DIR..."

cp feed-en/index.html "$DEPLOY_DIR/"
cp feed-en/rss.xml "$DEPLOY_DIR/"
cp feed-en/vercel.json "$DEPLOY_DIR/"

# Cover image (convert to jpg if possible, fallback to copy)
python3 -c "
from PIL import Image
img = Image.open('cover.png')
img = img.resize((600, 600), Image.LANCZOS)
img.save('$DEPLOY_DIR/cover.jpg', quality=80)
" 2>/dev/null || cp cover.png "$DEPLOY_DIR/cover.jpg"

# Episodes
mkdir -p "$DEPLOY_DIR/episodes/ep001"
mkdir -p "$DEPLOY_DIR/episodes/ep002"
mkdir -p "$DEPLOY_DIR/episodes/ep003"
cp episodes/ep001/episode-001-en.mp3 "$DEPLOY_DIR/episodes/ep001/"
cp episodes/ep002/episode-002-en.mp3 "$DEPLOY_DIR/episodes/ep002/"
cp episodes/ep003/ep003-en.mp3 "$DEPLOY_DIR/episodes/ep003/"

echo "Deploying to Vercel (moltcast-en)..."
cd "$DEPLOY_DIR"
vercel link --project moltcast-en --yes
vercel --prod --yes

rm -rf "$DEPLOY_DIR"
echo "Done! English feed: https://moltcast-en.vercel.app/rss.xml"
