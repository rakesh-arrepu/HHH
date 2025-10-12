import { ApolloClient, InMemoryCache, HttpLink, from } from '@apollo/client';
import { onError } from '@apollo/client/link/error';

const API_URL = import.meta.env.VITE_API_URL ?? 'http://localhost:8000';

const httpLink = new HttpLink({
  uri: `${API_URL}/graphql`,
  credentials: 'include',
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

export const client = new ApolloClient({
  link: from([errorLink, httpLink]),
  cache: new InMemoryCache(),
});
