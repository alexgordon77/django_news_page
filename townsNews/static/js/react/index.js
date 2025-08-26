import React from 'react';
import { createRoot } from 'react-dom/client';
import CustomTable from './components/CustomTable';

const App = () => {
    return (
        <div className="admin-dashboard">
            <h1>Ласкаво просимо до адмін панелі!</h1>
            <CustomTable endpoint="/api/articles/" />
        </div>
    );
};

const root = createRoot(document.getElementById('react-root'));
root.render(<App />);