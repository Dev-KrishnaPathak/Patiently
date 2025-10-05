const Header = () => {
  return (
    <header style={{ backgroundColor: 'white', borderBottom: '1px solid #e5e7eb' }}>
      <div style={{ maxWidth: 1120, margin: '0 auto', padding: '12px 16px' }}>
        {/* Minimal header - no links */}
        <div style={{ fontWeight: 600 }}>DocuSage</div>
      </div>
    </header>
  );
};

export default Header;
