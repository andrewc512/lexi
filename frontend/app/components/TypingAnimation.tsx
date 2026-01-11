"use client";

import { useState, useEffect } from "react";
import { SUPPORTED_LANGUAGES } from "@/types/language";

const LANGUAGES = SUPPORTED_LANGUAGES.map((lang) => lang.name);
const TYPING_SPEED = 100;
const DELETING_SPEED = 50;
const PAUSE_AFTER_TYPING = 2000;

export function TypingAnimation() {
  const [currentIndex, setCurrentIndex] = useState(0);
  const [displayText, setDisplayText] = useState("");
  const [isDeleting, setIsDeleting] = useState(false);

  useEffect(() => {
    const currentLanguage = LANGUAGES[currentIndex];
    let timeout: NodeJS.Timeout;

    // If we've finished typing, pause then start deleting
    if (!isDeleting && displayText === currentLanguage) {
      timeout = setTimeout(() => {
        setIsDeleting(true);
      }, PAUSE_AFTER_TYPING);
      return () => clearTimeout(timeout);
    }

    // If we've finished deleting, move to next language
    if (isDeleting && displayText === "") {
      setIsDeleting(false);
      setCurrentIndex((prev) => (prev + 1) % LANGUAGES.length);
      return;
    }

    // Continue typing or deleting
    const speed = isDeleting ? DELETING_SPEED : TYPING_SPEED;
    timeout = setTimeout(() => {
      if (!isDeleting) {
        // Typing forward
        setDisplayText(currentLanguage.slice(0, displayText.length + 1));
      } else {
        // Deleting backward
        setDisplayText(displayText.slice(0, -1));
      }
    }, speed);

    return () => clearTimeout(timeout);
  }, [displayText, isDeleting, currentIndex]);

  const currentLanguage = LANGUAGES[currentIndex];
  const isComplete = !isDeleting && displayText === currentLanguage;

  return (
    <span>
      Can you speak
      <br />
      <span className="text-blue-600">
        {displayText}
        {isComplete && "?"}
      </span>
      <span className="animate-pulse">|</span>
    </span>
  );
}
