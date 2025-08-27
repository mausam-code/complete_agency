import React from 'react';
import { Routes, Route } from 'react-router-dom';
import ProjectList from '../components/projects/ProjectList';

const ProjectsPage = () => {
  return (
    <Routes>
      <Route path="/" element={<ProjectList />} />
      <Route path="/*" element={<ProjectList />} />
    </Routes>
  );
};

export default ProjectsPage;
