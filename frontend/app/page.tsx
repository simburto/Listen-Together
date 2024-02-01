import YTPlayer from './players/YTPlayer'
import './page.css';

export default function Home() {
  return (
    <main className="flex min-h-screen flex-col items-center justify-between p-24">
      <div>
        <h1>
          Listen <b>Together</b>
        </h1>

        <YTPlayer />
      </div>
      
    </main>
  )
}
