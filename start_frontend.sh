cd frontend
# we need to upgrade nodejs version. ai recommends 18

# curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.7/install.sh | bash
# nvm install --lts
# nvm use --lts
# nvm use 24.13.1

# npm install @vue/tsconfig --save-dev

export VITE_API_URL='http://localhost:3000/api/v1'

npm install
npm run dev