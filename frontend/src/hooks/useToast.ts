export default function useToast(){
  return { addToast: (message:string, options?: {type?: string}) => console.log(`${options?.type || 'info'}: ${message}`) }
}
