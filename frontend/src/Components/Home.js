import React from 'react'
import Cards from './Cards'
import { useOutletContext } from 'react-router-dom';
function Home() {
    let { search=""} = useOutletContext();
    let users=[
        {
          "id": 7,
          "email": "michael.lawson@reqres.in",
          "first_name": "Michael",
          "last_name": "Lawson",
          "avatar": "https://reqres.in/img/faces/7-image.jpg"
        },
        {
          "id": 8,
          "email": "lindsay.ferguson@reqres.in",
          "first_name": "Lindsay",
          "last_name": "Ferguson",
          "avatar": "https://reqres.in/img/faces/8-image.jpg"
        },
        {
          "id": 9,
          "email": "tobias.funke@reqres.in",
          "first_name": "Tobias",
          "last_name": "Funke",
          "avatar": "https://reqres.in/img/faces/9-image.jpg"
        },
        {
          "id": 10,
          "email": "byron.fields@reqres.in",
          "first_name": "Byron",
          "last_name": "Fields",
          "avatar": "https://reqres.in/img/faces/10-image.jpg"
        },
        {
          "id": 11,
          "email": "george.edwards@reqres.in",
          "first_name": "George",
          "last_name": "Edwards",
          "avatar": "https://reqres.in/img/faces/11-image.jpg"
        },
        {
          "id": 12,
          "email": "rachel.howell@reqres.in",
          "first_name": "Rachel",
          "last_name": "Howell",
          "avatar": "https://reqres.in/img/faces/12-image.jpg"
        },
        {
          "id": 13,
          "email": "rachel.howell@reqres.in",
          "first_name": "Racheli",
          "last_name": "Howelli",
          "avatar": "https://reqres.in/img/faces/12-image.jpg"
        }
]
    let filteredUsers = users.filter(
        (user) =>
        user.first_name.toLowerCase().includes(search.toLowerCase()) ||
        user.last_name.toLowerCase().includes(search.toLowerCase())
    );
  return (
    <div className="container mt-5">
    <div className="row justify-content-center">
      {filteredUsers.map((user) => (
        <div className="col-md-4 mb-4" key={user.id}>
          <Cards user={user} />
        </div>
      ))}
    </div>
  </div>
  )
}

export default Home