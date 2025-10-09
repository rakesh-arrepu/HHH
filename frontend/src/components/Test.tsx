import { FC } from 'react';

interface TestProps {
  message: string;
}

export const Test: FC<TestProps> = ({ message }) => {
  return <div>{message}</div>;
};