import { useLayoutEffect, useRef, useState } from 'react';
import { gsap } from 'gsap';
import { GoArrowUpRight } from 'react-icons/go';
import './CardNav.css';

const CardNav = ({
    items,
    onNavigate,
    activeView,
    className = '',
    ease = 'power3.out',
}) => {
    const [isOpen, setIsOpen] = useState(false);
    const containerRef = useRef(null);
    const cardsRef = useRef([]);
    const tlRef = useRef(null);

    const createTimeline = () => {
        const el = containerRef.current;
        if (!el) return null;

        gsap.set(el, { height: 0, overflow: 'hidden', opacity: 0 });
        gsap.set(cardsRef.current, { y: 30, opacity: 0, scale: 0.95 });

        const tl = gsap.timeline({ paused: true });

        tl.to(el, {
            height: 'auto',
            opacity: 1,
            duration: 0.45,
            ease,
        });

        tl.to(
            cardsRef.current,
            {
                y: 0,
                opacity: 1,
                scale: 1,
                duration: 0.4,
                ease,
                stagger: 0.08,
            },
            '-=0.15'
        );

        return tl;
    };

    useLayoutEffect(() => {
        const tl = createTimeline();
        tlRef.current = tl;
        return () => {
            tl?.kill();
            tlRef.current = null;
        };
        // eslint-disable-next-line react-hooks/exhaustive-deps
    }, [ease, items]);

    useLayoutEffect(() => {
        const tl = tlRef.current;
        if (!tl) return;

        if (isOpen) {
            tl.play(0);
        } else {
            tl.reverse();
        }
    }, [isOpen]);

    const handleCardClick = (item) => {
        if (item.view && onNavigate) {
            onNavigate(item.view);
        }
    };

    const setCardRef = (i) => (el) => {
        if (el) cardsRef.current[i] = el;
    };

    return (
        <div className={`cardnav ${className}`}>
            {/* Toggle Button */}
            <button
                className={`cardnav-toggle ${isOpen ? 'open' : ''}`}
                onClick={() => setIsOpen(!isOpen)}
                aria-label={isOpen ? 'Close menu' : 'Open menu'}
            >
                <span className="cardnav-toggle-label">
                    {isOpen ? 'Close' : 'Explore'}
                </span>
                <div className="cardnav-hamburger">
                    <div className="cardnav-line" />
                    <div className="cardnav-line" />
                </div>
            </button>

            {/* Cards Container */}
            <div ref={containerRef} className="cardnav-cards">
                {(items || []).map((item, idx) => {
                    const isActive = activeView === item.view;
                    return (
                        <div
                            key={`${item.label}-${idx}`}
                            className={`cardnav-card ${isActive ? 'active' : ''}`}
                            ref={setCardRef(idx)}
                            style={{ backgroundColor: item.bgColor }}
                            onClick={() => handleCardClick(item)}
                        >
                            <div className="cardnav-card-header">
                                <span className="cardnav-card-icon">{item.icon}</span>
                                <span className="cardnav-card-label">{item.label}</span>
                                {isActive && <span className="cardnav-active-dot" />}
                            </div>
                            <p className="cardnav-card-desc">{item.description}</p>
                            {item.links && item.links.length > 0 && (
                                <div className="cardnav-card-links">
                                    {item.links.map((lnk, i) => (
                                        <span key={i} className="cardnav-card-link">
                                            <GoArrowUpRight className="cardnav-link-icon" />
                                            {lnk.label}
                                        </span>
                                    ))}
                                </div>
                            )}
                        </div>
                    );
                })}
            </div>
        </div>
    );
};

export default CardNav;
