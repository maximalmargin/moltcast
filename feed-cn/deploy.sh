#!/bin/bash
# Deploy MoltCast Chinese feed to Vercel
# Run from repo root: bash feed-cn/deploy.sh
set -e

DEPLOY_DIR=$(mktemp -d)
echo "Building Chinese feed in $DEPLOY_DIR..."

cp feed-cn/index.html "$DEPLOY_DIR/"
cp feed-cn/rss.xml "$DEPLOY_DIR/"
cp feed-cn/vercel.json "$DEPLOY_DIR/"

# Link to the correct Vercel project (moltcast-cn) to avoid creating new projects
mkdir -p "$DEPLOY_DIR/.vercel"
cat > "$DEPLOY_DIR/.vercel/project.json" << 'VERCEL'
{"projectId":"prj_Aixm728CCSW1uQB0jS4nt0FDsuF5","orgId":"team_d5T819OU3k5EZgtoFcGThgBX","projectName":"moltcast-cn"}
VERCEL

# Cover image (use Chinese cover)
python3 -c "
from PIL import Image
img = Image.open('cover-cn.png')
img = img.resize((600, 600), Image.LANCZOS)
img.save('$DEPLOY_DIR/cover.jpg', quality=80)
" 2>/dev/null || cp cover-cn.png "$DEPLOY_DIR/cover.jpg"

# Episodes
mkdir -p "$DEPLOY_DIR/episodes/ep001"
mkdir -p "$DEPLOY_DIR/episodes/ep002"
mkdir -p "$DEPLOY_DIR/episodes/ep003"
cp episodes/ep001/episode-001-cn.mp3 "$DEPLOY_DIR/episodes/ep001/"
cp episodes/ep002/episode-002-cn.mp3 "$DEPLOY_DIR/episodes/ep002/"
cp episodes/ep003/ep003-cn.mp3 "$DEPLOY_DIR/episodes/ep003/"

echo "Deploying to Vercel (moltcast-cn.maximalmargin.com)..."
cd "$DEPLOY_DIR"
vercel --prod --yes

rm -rf "$DEPLOY_DIR"
echo "Done! Chinese feed: https://moltcast-cn.maximalmargin.com/rss.xml"
