import React,{useState} from 'react'
import Navigation from './Components/Navigation'
import { Outlet } from 'react-router-dom'
import Footer from './Components/Footer'
function RootLayout() {
    let [search, getSearch] = useState("");
  return (
    <div>
        <Navigation search={search} getSearch={getSearch}/>
            <div style={{minHeight:'85vh'}}>
            <Outlet context={{search}} />
            </div>
        <Footer/>
    </div>
  )
}

export default RootLayout