import { ApolloClient, InMemoryCache, HttpLink, from } from '@apollo/client';
import { onError } from '@apollo/client/link/error';
import { setContext } from '@apollo/client/link/context';

const API_URL = import.meta.env.VITE_API_URL ?? 'http://localhost:8000';

const httpLink = new HttpLink({
  uri: `${API_URL}/graphql`,
  credentials: 'include',
  useGETForQueries: true,
});

const errorLink = onError((err: any) => {
  const { graphQLErrors, networkError } = err || {};
  if (graphQLErrors && Array.isArray(graphQLErrors)) {
    // eslint-disable-next-line no-console
    graphQLErrors.forEach((gqlErr: any) => {
      const { message, locations, path } = gqlErr || {};
      console.error(
        `[GraphQL error]: Message: ${message}, Location: ${JSON.stringify(locations)}, Path: ${path}`
      );
    });
  }
  if (networkError) {
    // eslint-disable-next-line no-console
    console.error(`[Network error]: ${String(networkError)}`);
  }
});

const getCookie = (name: string): string | null => {
  const match = document.cookie.match(new RegExp(`(^|; )${name}=([^;]*)`));
  return match ? decodeURIComponent(match[2]) : null;
};

const csrfLink = setContext((operation, prevContext) => {
  // Only attach CSRF header for non-Query operations
  const defs: any[] = (operation.query as any)?.definitions || [];
  const opDef = defs.find((d) => d.kind === 'OperationDefinition');
  const opType = opDef?.operation ?? 'query';
  if (opType === 'query') return {};
  const token = getCookie('hhh_csrf');
  if (!token) return {};
  return {
    headers: {
      ...(prevContext.headers || {}),
      'X-CSRF-Token': token,
    },
  };
});

export const client = new ApolloClient({
  link: from([errorLink, csrfLink, httpLink]),
  cache: new InMemoryCache(),
});
