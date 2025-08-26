import React, { useState, useEffect } from 'react';

const CustomTable = ({ endpoint }) => {
    const [data, setData] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    const [page, setPage] = useState(1);

    const fetchData = (page) => {
        setLoading(true);
        fetch(`${endpoint}?page=${page}`)
            .then(response => response.json())
            .then(data => {
                setData(data.results);
                setLoading(false);
            })
            .catch(err => {
                setError(err.message);
                setLoading(false);
            });
    };

    useEffect(() => {
        fetchData(page);
    }, [page]);

    return (
        <div className="custom-table">
            {loading ? <p>Завантаження...</p> : (
                <>
                    <table>
                        <thead>
                            <tr>
                                {Object.keys(data[0] || {}).map(key => <th key={key}>{key}</th>)}
                            </tr>
                        </thead>
                        <tbody>
                            {data.map((row, idx) => (
                                <tr key={idx}>
                                    {Object.values(row).map((value, index) => <td key={index}>{value}</td>)}
                                </tr>
                            ))}
                        </tbody>
                    </table>
                    <div className="pagination">
                        <button onClick={() => setPage(page - 1)} disabled={page === 1}>Попередня</button>
                        <button onClick={() => setPage(page + 1)}>Наступна</button>
                    </div>
                </>
            )}
            {error && <p>Помилка: {error}</p>}
        </div>
    );
};

export default CustomTable;