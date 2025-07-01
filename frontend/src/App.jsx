import { Routes, Route } from 'react-router-dom'
import { useEffect, useState } from 'react';
import Home from '@pages/home/Home'
import Configurator from '@pages/configurator/Configurator'
import Info from '@pages/info/Info'
import './App.css'

function App() {

  return (
    
    <>
      <Routes>
        <Route path='/' element={<Home/>}></Route>
        <Route path='/configurator' element={<Configurator/>}></Route> 
        <Route path='/info' element={<Info/>}></Route> 
      </Routes>
    </>

  )
}

export default App
