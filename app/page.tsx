"use client";

import { useMemo, useState } from "react";
import dashboardData from "./dashboard-data.json";

type ViewKey = "overview" | "category" | "sku" | "inventory" | "markdown" | "vendors";
type Action = "REORDER" | "MAINTAIN" | "TRANSFER" | "MARKDOWN" | "EXIT";

const views: { key: ViewKey; short: string; label: string; eyebrow: string }[] = [
  { key: "overview", short: "01", label: "Overview", eyebrow: "Trading performance" },
  { key: "category", short: "02", label: "Category", eyebrow: "Assortment productivity" },
  { key: "sku", short: "03", label: "SKU", eyebrow: "Action intelligence" },
  { key: "inventory", short: "04", label: "Inventory", eyebrow: "Allocation & transfers" },
  { key: "markdown", short: "05", label: "Markdown", eyebrow: "Seasonal exit" },
  { key: "vendors", short: "06", label: "Vendors", eyebrow: "Supplier portfolio" },
];

const money = (value: number, decimals = 1) => {
  if (Math.abs(value) >= 1_000_000) return `$${(value / 1_000_000).toFixed(decimals)}M`;
  if (Math.abs(value) >= 1_000) return `$${(value / 1_000).toFixed(0)}K`;
  return `$${value.toLocaleString("en-CA", { maximumFractionDigits: 0 })}`;
};
const percent = (value: number, signed = false) => `${signed && value > 0 ? "+" : ""}${(value * 100).toFixed(1)}%`;
const number = (value: number) => value.toLocaleString("en-CA");
const month = (value: string) => new Intl.DateTimeFormat("en-CA", { month: "short" }).format(new Date(`${value}-01T12:00:00`));

function ActionPill({ action }: { action: string }) {
  return <span className={`action-pill action-${action.toLowerCase()}`}>{action}</span>;
}

function Kpi({ label, value, note, tone = "gold" }: { label: string; value: string; note: string; tone?: "gold" | "sage" | "red" }) {
  return (
    <article className={`kpi-card tone-${tone}`}>
      <p>{label}</p>
      <strong>{value}</strong>
      <span>{note}</span>
    </article>
  );
}

function Panel({ title, note, children, className = "" }: { title: string; note?: string; children: React.ReactNode; className?: string }) {
  return (
    <section className={`panel ${className}`}>
      <header className="panel-header">
        <div>
          <p className="panel-kicker">{title}</p>
          {note && <span>{note}</span>}
        </div>
      </header>
      <div className="panel-body">{children}</div>
    </section>
  );
}

function TrendChart({ compact = false }: { compact?: boolean }) {
  const values = dashboardData.monthlyTrend.flatMap((item) => [item.actual, item.plan]);
  const min = Math.min(...values) * 0.88;
  const max = Math.max(...values) * 1.03;
  return (
    <div className={`trend-chart ${compact ? "compact" : ""}`} aria-label="Monthly actual sales compared with plan">
      <div className="chart-legend"><span className="actual-key">Actual</span><span className="plan-key">Plan</span></div>
      <div className="trend-grid">
        {dashboardData.monthlyTrend.map((item) => {
          const actual = Math.max(4, ((item.actual - min) / (max - min)) * 100);
          const plan = Math.max(4, ((item.plan - min) / (max - min)) * 100);
          return (
            <div className="trend-month" key={item.month}>
              <div className="trend-columns">
                <i className="actual-bar" style={{ height: `${actual}%` }} title={`Actual ${money(item.actual)}`} />
                <i className="plan-bar" style={{ height: `${plan}%` }} title={`Plan ${money(item.plan)}`} />
              </div>
              <span>{month(item.month)}</span>
            </div>
          );
        })}
      </div>
    </div>
  );
}

function OverviewView({ salesFactor }: { salesFactor: number }) {
  const kpis = dashboardData.kpis;
  const categoryMax = Math.max(...dashboardData.categories.slice(0, 7).map((item) => item.sales));
  const featuredActions = dashboardData.skus.slice(0, 7);
  return (
    <>
      <div className="kpi-grid five">
        <Kpi label="Net Sales" value={money(kpis.netSales * salesFactor)} note="FY2026 actual" />
        <Kpi label="Sales vs Plan" value={percent(kpis.salesVsPlan, true)} note="Ahead of plan" tone="sage" />
        <Kpi label="Gross Margin" value={percent(kpis.grossMargin)} note="+90 bps vs target" />
        <Kpi label="Sell-Through" value={percent(kpis.sellThrough)} note="13-week view" />
        <Kpi label="Inventory" value={money(kpis.inventoryValue)} note={`${kpis.weeksOfSupply.toFixed(1)} weeks of supply`} />
      </div>
      <div className="dashboard-grid overview-grid">
        <Panel title="Sales performance" note="Actual vs plan · FY2026" className="trend-panel"><TrendChart /></Panel>
        <Panel title="Category contribution" note="Net sales · leading categories">
          <div className="ranking-bars">
            {dashboardData.categories.slice(0, 7).map((item, index) => (
              <div className="ranking-row" key={item.name}>
                <span className="rank">{String(index + 1).padStart(2, "0")}</span>
                <span className="ranking-label">{item.name}</span>
                <div className="ranking-track"><i style={{ width: `${(item.sales / categoryMax) * 100}%` }} /></div>
                <strong>{money(item.sales)}</strong>
              </div>
            ))}
          </div>
        </Panel>
        <Panel title="Action intelligence" note="Highest-priority SKU decisions" className="wide-panel">
          <div className="table-scroll">
            <table className="data-table">
              <thead><tr><th>SKU</th><th>Product</th><th>Category</th><th>ST%</th><th>WOS</th><th>Inventory</th><th>Action</th></tr></thead>
              <tbody>{featuredActions.map((item) => <tr key={item.sku}><td className="mono">{item.sku}</td><td>{item.product}</td><td>{item.category}</td><td>{percent(item.sellThrough)}</td><td>{item.wos.toFixed(1)}</td><td>{money(item.inventory, 0)}</td><td><ActionPill action={item.action} /></td></tr>)}</tbody>
            </table>
          </div>
        </Panel>
        <aside className="management-note">
          <span>WEEK 32 READOUT</span>
          <h3>Invest in light. Rebalance before markdown.</h3>
          <p>Lighting leads assortment productivity while premium furniture absorbs a disproportionate share of inventory. Protect availability in high-demand stores and transfer slow-moving stock before taking margin action.</p>
          <a href="#case-study">View the business case <span aria-hidden="true">↘</span></a>
        </aside>
      </div>
    </>
  );
}

function CategoryView() {
  const categoryMax = Math.max(...dashboardData.categories.map((item) => item.salesPerSku));
  const top = dashboardData.categories.slice(0, 14);
  return (
    <div className="dashboard-grid category-grid">
      <Panel title="Sales vs inventory share" note="Investment signals by category" className="wide-panel">
        <div className="table-scroll">
          <table className="data-table category-table">
            <thead><tr><th>Category</th><th>SKUs</th><th>Sales</th><th>Sales share</th><th>Inventory share</th><th>Sales / SKU</th><th>Signal</th></tr></thead>
            <tbody>{top.map((item) => {
              const delta = item.salesShare - item.inventoryShare;
              const signal = delta > 0.02 ? "INVEST" : delta < -0.02 ? "REDUCE" : "HOLD";
              return <tr key={item.name}><td>{item.name}</td><td>{item.skuCount}</td><td>{money(item.sales)}</td><td>{percent(item.salesShare)}</td><td>{percent(item.inventoryShare)}</td><td>{money(item.salesPerSku)}</td><td><ActionPill action={signal} /></td></tr>;
            })}</tbody>
          </table>
        </div>
      </Panel>
      <Panel title="Assortment productivity" note="Net sales generated per active SKU">
        <div className="productivity-list">
          {dashboardData.categories.slice(0, 9).map((item) => (
            <div key={item.name}><div><span>{item.name}</span><strong>{money(item.salesPerSku)}</strong></div><i><b style={{ width: `${(item.salesPerSku / categoryMax) * 100}%` }} /></i></div>
          ))}
        </div>
      </Panel>
      <Panel title="Price architecture" note="Demand by Entry / Good / Better / Best">
        <div className="price-bands">
          {dashboardData.priceBands.map((item, index) => <article key={item.name}><span>0{index + 1}</span><h4>{item.name}</h4><strong>{money(item.sales)}</strong><p>{percent(item.sellThrough)} sell-through</p><i><b style={{ width: `${item.sellThrough * 100}%` }} /></i></article>)}
        </div>
      </Panel>
      <aside className="insight-banner wide-panel">
        <span>MERCHANDISE DECISION</span>
        <h3>Lighting earns more from less.</h3>
        <p>Floor lamps, pendants and table lamps combine strong sales per SKU with a lower share of inventory. Expand selectively while reducing depth in slower premium furniture and decorative objects.</p>
      </aside>
    </div>
  );
}

function SkuView() {
  const [query, setQuery] = useState("");
  const [action, setAction] = useState("ALL");
  const visible = useMemo(() => dashboardData.skus.filter((item) => {
    const matchesText = `${item.sku} ${item.product} ${item.category}`.toLowerCase().includes(query.toLowerCase());
    return matchesText && (action === "ALL" || item.action === action);
  }).slice(0, 18), [query, action]);
  const quadrantItems = dashboardData.skus.filter((item) => item.action !== "MAINTAIN").slice(0, 28);
  return (
    <div className="dashboard-grid sku-grid">
      <Panel title="SKU decision matrix" note="Sell-through × weeks of supply" className="quadrant-panel">
        <div className="quadrant" aria-label="SKU sell-through and weeks-of-supply matrix">
          <div className="quad-label q1">REPLENISH</div><div className="quad-label q2">HEALTHY</div><div className="quad-label q3">TRANSFER / MARKDOWN</div><div className="quad-label q4">EXIT</div>
          <span className="axis-y">SELL-THROUGH</span><span className="axis-x">WEEKS OF SUPPLY</span>
          {quadrantItems.map((item, index) => {
            const left = Math.min(91, Math.max(7, (item.wos / 100) * 86));
            const top = Math.min(89, Math.max(7, (1 - item.sellThrough) * 88));
            return <i className={`bubble bubble-${item.action.toLowerCase()}`} style={{ left: `${left}%`, top: `${top}%`, width: `${8 + (index % 4) * 2}px`, height: `${8 + (index % 4) * 2}px` }} key={item.sku} title={`${item.product}: ${item.action}`} />;
          })}
        </div>
      </Panel>
      <Panel title="Decision filters" note={`${visible.length} priority SKUs shown`} className="filter-panel">
        <label className="search-label"><span>Search assortment</span><input value={query} onChange={(event) => setQuery(event.target.value)} placeholder="SKU, product or category" /></label>
        <div className="action-filters">
          {["ALL", "REORDER", "TRANSFER", "MARKDOWN", "EXIT"].map((item) => <button className={action === item ? "active" : ""} onClick={() => setAction(item)} key={item}>{item}</button>)}
        </div>
        <div className="action-counts">
          {Object.entries(dashboardData.actionCounts).filter(([key]) => key !== "MAINTAIN").map(([key, value]) => <div key={key}><ActionPill action={key} /><strong>{value}</strong></div>)}
        </div>
      </Panel>
      <Panel title="SKU trading book" note="Exception-based merchandise action" className="wide-panel">
        <div className="table-scroll tall-table"><table className="data-table"><thead><tr><th>SKU</th><th>Product</th><th>Category</th><th>Net sales</th><th>Margin</th><th>ST%</th><th>WOS</th><th>Action</th></tr></thead><tbody>{visible.map((item) => <tr key={item.sku}><td className="mono">{item.sku}</td><td>{item.product}</td><td>{item.category}</td><td>{money(item.sales, 0)}</td><td>{percent(item.margin)}</td><td>{percent(item.sellThrough)}</td><td>{item.wos.toFixed(1)}</td><td><ActionPill action={item.action} /></td></tr>)}</tbody></table></div>
      </Panel>
    </div>
  );
}

function InventoryView() {
  const maxInventory = Math.max(...dashboardData.stores.map((item) => item.inventory));
  const avgWos = dashboardData.stores.reduce((sum, item) => sum + item.wos, 0) / dashboardData.stores.length;
  const transferUnits = dashboardData.transfers.reduce((sum, item) => sum + item.units, 0);
  return (
    <>
      <div className="kpi-grid four">
        <Kpi label="Inventory Investment" value={money(dashboardData.kpis.inventoryValue)} note="At product cost" />
        <Kpi label="Network WOS" value={dashboardData.kpis.weeksOfSupply.toFixed(1)} note="Target 5.5 weeks" tone="red" />
        <Kpi label="Transfer Opportunity" value={`${transferUnits} units`} note={`${dashboardData.transfers.length} priority moves`} tone="sage" />
        <Kpi label="Stock Turn" value={`${dashboardData.kpis.stockTurn.toFixed(1)}×`} note="Annualized" />
      </div>
      <div className="dashboard-grid inventory-grid">
        <Panel title="Store inventory position" note={`Average ${avgWos.toFixed(1)} WOS`}>
          <div className="store-heatmap">
            {dashboardData.stores.map((item) => <article key={item.id} style={{ "--heat": item.inventory / maxInventory } as React.CSSProperties}><span>{item.tier}</span><h4>{item.name}</h4><strong>{money(item.inventory)}</strong><p>{item.wos.toFixed(1)} WOS</p></article>)}
          </div>
        </Panel>
        <Panel title="Inventory rebalancing" note="Move stock before taking markdown" className="wide-panel">
          <div className="transfer-flow-list">
            {dashboardData.transfers.map((item, index) => <article key={`${item.sku}-${index}`}><span className="transfer-index">{String(index + 1).padStart(2, "0")}</span><div><small>{item.sku}</small><h4>{item.product}</h4></div><div className="store-node"><small>FROM</small><strong>{item.from}</strong><span>{item.fromWos.toFixed(1)} WOS</span></div><div className="transfer-arrow"><b>{item.units}</b><span>UNITS</span></div><div className="store-node"><small>TO</small><strong>{item.to}</strong><span>{item.toWos.toFixed(1)} WOS</span></div></article>)}
          </div>
        </Panel>
        <aside className="management-note inventory-note"><span>ALLOCATION RULE</span><h3>Demand leads the move.</h3><p>Transfers prioritize a four-week cover in receiving stores while keeping donor locations above a healthy post-transfer threshold.</p></aside>
      </div>
    </>
  );
}

function MarkdownView() {
  const markdownSkus = dashboardData.skus.filter((item) => item.action === "MARKDOWN" || item.action === "EXIT").slice(0, 10);
  const velocityMax = Math.max(dashboardData.markdown.beforeVelocity, dashboardData.markdown.afterVelocity);
  return (
    <div className="dashboard-grid markdown-grid">
      <Panel title="Markdown effectiveness" note="Average weekly sales velocity">
        <div className="velocity-comparison">
          <article><span>PRE-MARKDOWN</span><strong>{dashboardData.markdown.beforeVelocity.toFixed(1)}</strong><p>units / week</p><i><b style={{ height: `${(dashboardData.markdown.beforeVelocity / velocityMax) * 100}%` }} /></i></article>
          <article className="after"><span>POST-MARKDOWN</span><strong>{dashboardData.markdown.afterVelocity.toFixed(1)}</strong><p>units / week</p><i><b style={{ height: `${(dashboardData.markdown.afterVelocity / velocityMax) * 100}%` }} /></i></article>
          <div className="velocity-lift"><small>VELOCITY LIFT</small><strong>{percent(dashboardData.markdown.velocityLift, true)}</strong><span>{number(dashboardData.markdown.inventoryCleared)} units cleared</span></div>
        </div>
      </Panel>
      <Panel title="Seasonal performance" note="Plan vs actual and next-season action">
        <div className="seasonal-list">
          {dashboardData.seasonal.map((item) => <article key={item.name}><div><h4>{item.name}</h4><span>{money(item.actual)} actual</span></div><strong className={item.variance < 0 ? "negative" : "positive"}>{percent(item.variance, true)}</strong><i><b style={{ width: `${Math.min(100, item.actual / Math.max(item.actual, item.plan) * 100)}%` }} /></i></article>)}
        </div>
      </Panel>
      <Panel title="Markdown candidates" note="Staged exit actions" className="wide-panel">
        <div className="table-scroll"><table className="data-table"><thead><tr><th>SKU</th><th>Product</th><th>Category</th><th>Sales</th><th>ST%</th><th>WOS</th><th>Inventory</th><th>Action</th></tr></thead><tbody>{markdownSkus.map((item) => <tr key={item.sku}><td className="mono">{item.sku}</td><td>{item.product}</td><td>{item.category}</td><td>{money(item.sales, 0)}</td><td>{percent(item.sellThrough)}</td><td>{item.wos.toFixed(1)}</td><td>{money(item.inventory, 0)}</td><td><ActionPill action={item.action} /></td></tr>)}</tbody></table></div>
      </Panel>
      <aside className="insight-banner wide-panel"><span>EXIT STRATEGY</span><h3>Clear with discipline, not panic.</h3><p>Use staged markdowns on end-of-season inventory after transfer opportunities are exhausted. Increase next-season Christmas décor commitment by approximately 12% and reduce winter comfort exposure.</p></aside>
    </div>
  );
}

function VendorView() {
  const topScore = Math.max(...dashboardData.vendors.map((item) => item.score));
  return (
    <div className="dashboard-grid vendor-grid">
      <Panel title="Vendor portfolio ranking" note="Commercial + operational score" className="wide-panel">
        <div className="vendor-list">
          {dashboardData.vendors.slice(0, 12).map((item, index) => <article key={item.id}><span className="vendor-rank">{String(index + 1).padStart(2, "0")}</span><div className="vendor-name"><small>{item.id}</small><h4>{item.name}</h4></div><div><small>SALES</small><strong>{money(item.sales)}</strong></div><div><small>MARGIN</small><strong>{percent(item.margin)}</strong></div><div><small>ON-TIME</small><strong>{percent(item.onTime)}</strong></div><div className="vendor-score"><i><b style={{ width: `${(item.score / topScore) * 100}%` }} /></i><strong>{item.score}</strong><span>/100</span></div></article>)}
        </div>
      </Panel>
      <Panel title="Commercial performance" note="Sales and margin by leading partner">
        <div className="commercial-bars">{dashboardData.vendors.slice(0, 7).map((item) => <div key={item.id}><span>{item.name}</span><i><b style={{ width: `${item.margin * 100}%` }} /></i><strong>{percent(item.margin)}</strong></div>)}</div>
      </Panel>
      <aside className="management-note vendor-note"><span>SUPPLIER ACTION</span><h3>Reward reliability.</h3><p>Concentrate future buying with partners that combine productive assortment, healthy margin and dependable delivery. Place low-service vendors on a 90-day corrective action plan.</p></aside>
    </div>
  );
}

export default function Home() {
  const [activeView, setActiveView] = useState<ViewKey>("overview");
  const [period, setPeriod] = useState("YTD");
  const [region, setRegion] = useState("All regions");
  const view = views.find((item) => item.key === activeView) ?? views[0];
  const salesFactor = period === "13 weeks" ? 0.38 : 1;
  const renderView = () => {
    if (activeView === "overview") return <OverviewView salesFactor={salesFactor} />;
    if (activeView === "category") return <CategoryView />;
    if (activeView === "sku") return <SkuView />;
    if (activeView === "inventory") return <InventoryView />;
    if (activeView === "markdown") return <MarkdownView />;
    return <VendorView />;
  };
  return (
    <main className="site-shell">
      <aside className="side-nav" aria-label="Dashboard navigation">
        <a className="brand-mark" href="#top" aria-label="Northstar Home and Living"><b>N</b><span>NORTHSTAR</span></a>
        <nav>{views.map((item) => <button key={item.key} className={activeView === item.key ? "active" : ""} onClick={() => { setActiveView(item.key); window.scrollTo({ top: 0, behavior: "smooth" }); }}><span>{item.short}</span>{item.label}</button>)}</nav>
        <a className="case-link" href="#case-study"><span>07</span>Case study</a>
        <div className="nav-footer"><span>FY26</span><small>WEEK 32</small></div>
      </aside>
      <div className="main-column" id="top">
        <header className="dashboard-header">
          <div className="mobile-brand"><b>N</b><span>NORTHSTAR</span></div>
          <div className="header-title"><p>{view.short} · {view.eyebrow}</p><h1>{view.label === "Overview" ? "Merchandise Trading Overview" : `${view.label} Performance`}</h1><span>FY2026 · Week 32 · Canadian Retail Division</span></div>
          <div className="header-controls">
            <label><span>PERIOD</span><select value={period} onChange={(event) => setPeriod(event.target.value)}><option>YTD</option><option>13 weeks</option></select></label>
            <label><span>REGION</span><select value={region} onChange={(event) => setRegion(event.target.value)}><option>All regions</option><option>Atlantic</option><option>Central</option></select></label>
            <div className="refresh"><span>LAST REFRESHED</span><strong>12 AUG 2026</strong></div>
          </div>
        </header>
        <div className="mobile-nav" aria-label="Mobile dashboard navigation">{views.map((item) => <button key={item.key} className={activeView === item.key ? "active" : ""} onClick={() => setActiveView(item.key)}>{item.label}</button>)}</div>
        <section className="view-stage" aria-live="polite">{renderView()}</section>

        <section className="case-study" id="case-study">
          <div className="case-intro"><p>PORTFOLIO CASE STUDY · CHELAKA FERNANDO</p><h2>Merchandise Planning<br /><em>& Assortment Optimization</em></h2><p className="case-deck">A complete decision-support system for a fictional 10-store Canadian retailer—built to answer what to buy, how much to buy, where to allocate it, when to replenish it, and when to exit.</p></div>
          <div className="case-metrics"><div><strong>{number(dashboardData.meta.skus)}</strong><span>SKUs</span></div><div><strong>{number(dashboardData.meta.transactions)}</strong><span>Transactions</span></div><div><strong>{dashboardData.meta.stores}</strong><span>Stores</span></div><div><strong>18</strong><span>SQL analyses</span></div></div>
          <div className="case-sections">
            <article><span>01</span><div><p>THE CHALLENGE</p><h3>Inventory was in the wrong place.</h3><p>High-performing products stocked out in priority locations while identical merchandise accumulated elsewhere. Planning relied on disconnected spreadsheets and reactive markdown decisions.</p></div></article>
            <article><span>02</span><div><p>THE SOLUTION</p><h3>One commercial operating system.</h3><p>The model connects assortment, open-to-buy, allocation, replenishment, transfers, markdowns, seasonal planning and vendor performance through one auditable retail dataset.</p></div></article>
            <article><span>03</span><div><p>THE ANALYSIS</p><h3>Decisions, not decorative charts.</h3><p>Every KPI leads to action: replenish, maintain, transfer, markdown or exit. The trading view isolates exceptions so a merchandiser can decide what changes this week.</p></div></article>
            <article><span>04</span><div><p>THE IMPACT</p><h3>Margin protected before inventory is cleared.</h3><p>Transfer recommendations rebalance store cover, staged markdown logic improves exit discipline, and open-to-buy controls protect future purchasing capacity.</p></div></article>
          </div>
          <div className="architecture">
            <div className="architecture-copy"><p>DATA MODEL</p><h3>Seven tables. One retail truth.</h3><p>A product-centred star schema joins transaction, inventory, purchase-order and markdown facts to store and vendor dimensions.</p><div className="tech-row"><span>EXCEL</span><span>SQL</span><span>PYTHON</span><span>POWER BI LOGIC</span><span>WEB</span></div></div>
            <div className="schema" aria-label="Retail merchandising data model"><div className="schema-dim product">DIM_PRODUCT</div><div className="schema-fact sales">FACT_SALES</div><div className="schema-fact inventory">FACT_INVENTORY</div><div className="schema-fact purchase">FACT_PURCHASE_ORDERS</div><div className="schema-dim store">DIM_STORE</div><div className="schema-fact markdowns">FACT_MARKDOWNS</div><div className="schema-dim vendor">DIM_VENDOR</div></div>
          </div>
          <section className="findings"><div className="section-number">05</div><div><p>KEY FINDINGS</p><h3>Where management should move next.</h3><div className="finding-grid"><article><strong>01</strong><h4>Increase lighting depth</h4><p>Floor lamps and pendants deliver leading sales per SKU with comparatively lean inventory investment.</p></article><article><strong>02</strong><h4>Rebalance before markdown</h4><p>Eight priority transfers place seasonal and décor units into stores with proven demand.</p></article><article><strong>03</strong><h4>Control premium exposure</h4><p>Furniture drives sales but holds an outsized share of inventory and needs tighter receipt phasing.</p></article><article><strong>04</strong><h4>Back Christmas demand</h4><p>Actual sales outpaced plan by 18.3%; next-season commitment can increase approximately 12%.</p></article></div></div></section>
          <section className="project-files" id="project-files"><div><p>PROJECT FILES</p><h3>Open the complete planning system.</h3><span>Formula-driven workbooks, reproducible synthetic data, SQL analysis and executive reporting.</span></div><div className="file-links"><a href="/downloads/Merchandise_Planning_Model.xlsx" download><span>01</span><div><strong>Merchandise Planning Model</strong><small>Excel · 12 planning sheets</small></div><b>↓</b></a><a href="/downloads/Weekly_Merchandise_Trading_Report.pdf" target="_blank"><span>02</span><div><strong>Weekly Trading Report</strong><small>PDF · 4-page executive brief</small></div><b>↗</b></a><a href="/downloads/Data_Dictionary.pdf" target="_blank"><span>03</span><div><strong>Data Dictionary</strong><small>PDF · schema, fields and KPIs</small></div><b>↗</b></a><a className="github-placeholder" href="https://github.com/chelakafernando102/northstar-merchandise-intelligence" target="_blank" rel="noreferrer"><span>04</span><div><strong>GitHub Repository</strong><small>Source, data, SQL, DAX and documentation</small></div><b>↗</b></a></div></section>
        </section>
        <footer><span>NORTHSTAR HOME & LIVING · FICTIONAL PORTFOLIO PROJECT</span><span>DESIGNED & BUILT BY CHELAKA FERNANDO · 2026</span></footer>
      </div>
    </main>
  );
}
