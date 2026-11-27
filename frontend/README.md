# InsightX Frontend

Independent Vite + React frontend for InsightX.

## Local development

~~~bash
npm install
npm run assets:download
npm run dev
~~~

The asset sync command downloads the site's self-hosted media bundle into public/. It is required once after a fresh clone.

## Production build

~~~bash
npm run assets:download
npm run build
~~~

The static build is generated in dist/. The root Render Blueprint runs the asset sync step before building. The API URL defaults to https://insightx-analytics-api.onrender.com and can be changed in the CSV workspace section.
