import React from 'react';
import { SVGProps } from 'react';

type IconComponent = {
  (props: SVGProps<SVGSVGElement>): React.ReactElement;
  displayName?: string;
};

declare module 'react-icons/lib/index' {
  export type IconType = (props: any) => React.ReactElement;
}

declare module 'react-icons/fa' {
  export const FaRoute: IconComponent;
  export const FaMapMarkerAlt: IconComponent;
  export const FaClock: IconComponent;
  export const FaBuilding: IconComponent;
  export const FaUser: IconComponent;
  export const FaTruck: IconComponent;
  export const FaBox: IconComponent;
  export const FaFileAlt: IconComponent;
  export const FaSpinner: IconComponent;
  export const FaExclamationTriangle: IconComponent;
  export const FaRuler: IconComponent;
  export const FaShieldAlt: IconComponent;
  export const FaCheckCircle: IconComponent;
  export const FaExclamationCircle: IconComponent;
  export const FaTimesCircle: IconComponent;
  export const FaMap: IconComponent;
  export const FaGasPump: IconComponent;
  export const FaBed: IconComponent;
  export const FaChartLine: IconComponent;
}

declare module 'react-icons/fi' {
  export const FiClock: IconComponent;
}

declare module 'react-icons/hi2' {
  export const HiOutlineClipboardDocumentList: IconComponent;
}

