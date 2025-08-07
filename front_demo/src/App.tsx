import React from 'react';
import { Layout, Menu } from 'antd';
import { BrowserRouter as Router, Route, Routes, Link, useLocation } from 'react-router-dom';
import StrategyList from './pages/StrategyList';
import Account from './pages/Account';
import Market from './pages/Market';
import Log from './pages/Log';
import Dashboard from './pages/Dashboard';
import HummingbotTest from './pages/HummingbotTest';
import 'antd/dist/reset.css';

const { Header, Content } = Layout;

const Navigation: React.FC = () => {
  const location = useLocation();
  
  const menuItems = [
    { key: '/', label: '总览', path: '/' },
    { key: '/strategies', label: '策略管理', path: '/strategies' },
    { key: '/accounts', label: '账户管理', path: '/accounts' },
    { key: '/market', label: '行情', path: '/market' },
    { key: '/logs', label: '日志', path: '/logs' },
    { key: '/hummingbot-test', label: 'Hummingbot测试', path: '/hummingbot-test' },
  ];

  return (
    <Menu
      theme="dark"
      mode="horizontal"
      selectedKeys={[location.pathname]}
      items={menuItems.map(item => ({
        key: item.key,
        label: <Link to={item.path}>{item.label}</Link>,
      }))}
    />
  );
};

const App: React.FC = () => {
  return (
    <Router>
      <Layout style={{ minHeight: '100vh' }}>
        <Header>
          <Navigation />
        </Header>
        <Content style={{ padding: '24px' }}>
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/strategies" element={<StrategyList />} />
            <Route path="/accounts" element={<Account />} />
            <Route path="/market" element={<Market />} />
            <Route path="/logs" element={<Log />} />
            <Route path="/hummingbot-test" element={<HummingbotTest />} />
          </Routes>
        </Content>
      </Layout>
    </Router>
  );
};

export default App;
