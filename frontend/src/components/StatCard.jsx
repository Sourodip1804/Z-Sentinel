export default function StatCard({title, value, hint, icon}){
    return (
        <div className="stat-card">
            <div className="stat-top">
                <span>
                    {icon}
                </span>
                <span className="stat-title">
                    {title}
                </span>
            </div>
        </div>
    )
}