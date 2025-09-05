import { TestBed } from '@angular/core/testing';

import { GetNodesService } from './get-nodes.service';

describe('GetNodesService', () => {
  let service: GetNodesService;

  beforeEach(() => {
    TestBed.configureTestingModule({});
    service = TestBed.inject(GetNodesService);
  });

  it('should be created', () => {
    expect(service).toBeTruthy();
  });
});
