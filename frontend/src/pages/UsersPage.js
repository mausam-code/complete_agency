import React from 'react';
import { Routes, Route } from 'react-router-dom';
import UserList from '../components/users/UserList';

const UsersPage = () => {
  return (
    <Routes>
      <Route path="/" element={<UserList />} />
      <Route path="/*" element={<UserList />} />
    </Routes>
  );
};

export default UsersPage;
