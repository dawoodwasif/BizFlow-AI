
import React from "react";

const LoadingDots = () => {
  return (
    <div className="flex space-x-1.5 items-center">
      <div className="w-2 h-2 rounded-full bg-gray-400 animate-[bounce_1.4s_ease-in-out_0s_infinite]"></div>
      <div className="w-2 h-2 rounded-full bg-gray-400 animate-[bounce_1.4s_ease-in-out_0.2s_infinite]"></div>
      <div className="w-2 h-2 rounded-full bg-gray-400 animate-[bounce_1.4s_ease-in-out_0.4s_infinite]"></div>
    </div>
  );
};

export default LoadingDots;
