const AIAvatar = () => (
  <div className="msg-av ai">
    <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <path d="M12 2l2.4 7.4H22l-6.2 4.5 2.4 7.4L12 17l-6.2 4.3 2.4-7.4L2 9.4h7.6z"/>
    </svg>
  </div>
);

const UserAvatar = () => (
  <div className="msg-av user">You</div>
);

export default function ChatMessage({ message }) {
  const isUser = message.role === 'user';
  return (
    <div className={`msg-row ${isUser ? 'user' : 'ai'}`}>
      {isUser ? <UserAvatar /> : <AIAvatar />}
      <div className={`msg-bub ${isUser ? 'user' : 'ai'}${message.isError ? ' error' : ''}`}>
        {message.content}
      </div>
    </div>
  );
}
