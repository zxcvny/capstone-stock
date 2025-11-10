import { useState, useEffect } from "react";

function StockList() {
    const [stockData, setStockData] = useState({});
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    // 1분마다 데이터 가져옴
    const fetchData = async () => {
        try {
            const response = await fetch('http://localhost:8000/stocks/nasdaq100-quotes');
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            const data = await response.json();

            setStockData(data);
            setError(null);
        } catch (e) {
            console.error("데이터 불러오기 실패:", e);
            setError("데이터를 불러오는 데 실패했습니다. API 한도 초과 또는 서버 문제")
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        // 컴포넌트 마운트 시 즉시 1회 실행
        fetchData();

        // 60초(60000ms)마다 fetchData 함수 호출
        // const intervalId = setInterval(fetchData, 60000);

        // 컴포넌트 언마운트 시 인터벌 정리
        // return () => clearInterval(intervalId);
    }, []);

    if (loading) {
        return <div>로딩 중...</div>
    }

    if (error) {
        return <div>{error}</div>
    }

    const sortedData = Object.values(stockData).sort((a, b) =>
        a.symbol.localeCompare(b.symbol)
    );

    return (
        <div className="stock-grid">
            {sortedData.map((stock) => (
                <div
                 key={stock.symbol}
                 className="stock-card"
                 onClick={() => alert("test")}
                >
                    <div className="stock-header">
                        <span className="stock-symbol">{stock.symbol}</span>
                        <span className="stock-name">{stock.name || 'N/A'}</span>
                    </div>

                    <div className="stock-body">
                        <span className="stock-price">
                            ${parseFloat(stock.close || 0).toFixed(2)}
                        </span>
                        <span>{parseFloat(stock.percent_change || 0).toFixed(2)}</span>
                    </div>
                </div>
            ))}
        </div>
    )
}
export default StockList;